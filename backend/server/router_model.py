import threading
import traceback
from typing import Optional
from fastapi import APIRouter

from data_type.civitai_model_version import CivitaiModelVersion, CivitaiFileToDownload
from data_type.whatsai_model_downloading_info import ModelDownloadingInfo
from misc.constants import webui_model_dirs_map, comfyui_model_dirs_map
from misc.helpers import (
    gen_file_sha256,
    get_file_created_timestamp_and_datetime,
    get_file_size_in_kb
)
from misc.logger import logger
from tiny_db.helpers import SortType, sort_model_info
from tiny_db.model_dir import ModelDirTable
from tiny_db.model_downloading_info import ModelDownloadInfoTable
from tiny_db.model_type import ModelTypeTable
from data_type.base import PydanticModel
from tiny_db.model_info import ModelInfoTable
from misc.helpers_civitai import (
    get_image_url_of_civitai_model_info,
    get_civitai_model_info_by_hash,
    file_to_download_2_model_download_info,
    download_civitai_model_task,
    download_civitai_image_to_whatsai_file_dir
)


router = APIRouter()

@router.get('/get_all_model_types')
async def get_all_model_types():
    return await ModelTypeTable.all_model_types()

@router.get('/model_infos_by_type')
async def model_infos_by_type(
        model_type: str | None = None,
        sort_type: SortType = 'created_reverse',
        base_model_filter: str | None = None
):
    """ Get model infos by type, used by frontend to select. If no model_type, all models will be return. """
    results = await ModelInfoTable.get_model_info_by_model_type(model_type)
    if base_model_filter:
        results = filter(
            lambda s: s.get('base_model') and base_model_filter.lower() in s.get('base_model').lower()
            , results
        )

    return sort_model_info(results, sort_type)


class SyncModelInfosReq(PydanticModel):
    model_type: Optional[str] = None
    force_renew: bool = True


@router.post('/sync_model_infos')
async def sync_model_infos(req: SyncModelInfosReq):
    """ Sync model infos by type, if no model_type, all model infos will sync.
        We need it when user first setup or he/she put file in some dir manually.
    """

    model_type = req.model_type.lower()
    force_renew = req.force_renew

    if not model_type:
        model_dir_records = await ModelDirTable.get_all_model_dir_records()
    else:
        model_dir_records = await ModelDirTable.get_model_dir_records(model_type)

    model_infos = []
    for record in model_dir_records:
        model_file_paths = []

        # The reason we get the model_type again is that, model_type passed by the function can be None,
        # and we got from civitai is not used in whatsai system, so we must depend on dir as model_type
        # then sent for subsequent using.
        model_type, dirs = record.get('model_type'), record.get('dirs')
        for dir_path in dirs:
            files_in_dir = ModelDirTable.sync_get_model_files_in_dir(dir_path)
            model_file_paths.extend(files_in_dir)

        for model_file_path in model_file_paths:
            model_info = await _sync_single_model_info(model_type, model_file_path, force_renew)
            if model_info:
                model_infos.append(model_info)

    return sort_model_info(model_infos)


class SyncSingeModelInfoReq(PydanticModel):
    model_type: str
    model_file_path: str
    force_renew: bool = True

@router.post('/sync_single_model_info')
async def sync_single_model_info(req: SyncSingeModelInfoReq):
    model_type = req.model_type
    model_file_path = req.model_file_path
    force_renew = req.force_renew
    return await _sync_single_model_info(model_type, model_file_path, force_renew)

async def _sync_single_model_info(model_type: str, model_file_path: str, force_renew: bool):
    hash_str = await gen_file_sha256(model_file_path)
    assert hash_str, "Hash str: {} must not be empty.".format(hash_str)

    civitai_model_info, info = await get_civitai_model_info_by_hash(hash_str)

    civitai_model = None
    if civitai_model_info:
        try:
            civitai_model = CivitaiModelVersion(**civitai_model_info)
        except Exception as e:
            logger.error("parse civit model info error", e)
    else:
        logger.debug("no civit info found: {}".format(model_file_path), info)

    local_image_path = None
    if civitai_model:
        image_url = await get_image_url_of_civitai_model_info(civitai_model_info)
        if image_url:
            local_image_path = await download_civitai_image_to_whatsai_file_dir(image_url)

    time_stamp, datetime_str = get_file_created_timestamp_and_datetime(model_file_path)
    size_kb = get_file_size_in_kb(model_file_path)

    model_info = await ModelInfoTable.add_model_info(
        hash_str=hash_str,
        file_path=model_file_path,
        model_type=model_type,
        image_path=local_image_path,
        civitai_model=civitai_model,
        size_kb=size_kb,
        created_time_stamp=time_stamp,
        created_datetime_str=datetime_str,
        force_renew=force_renew
    )
    return model_info


@router.get('/get_all_models')
async def get_all_models(sort_type: SortType = 'created_reverse'):
    """ Get all models in tiny db, rearrange them in type of:
        { 'model_type': [model_info_1, model_info_1 ... ]
    """
    model_infos = await ModelInfoTable.get_all_models()

    # init models info in array by model type
    model_types = await ModelTypeTable.all_model_types()
    models_by_type_dict = {model_type: [] for model_type in model_types}

    for model_info in model_infos:
        model_type = model_info.get('model_type', "").lower()
        if model_type:
            models_in_model_type = models_by_type_dict.get(model_type, [])
            models_in_model_type.append(model_info)
            models_by_type_dict[model_type] = models_in_model_type

    # rearrange them in array
    list_results = []
    for k, v in models_by_type_dict.items():
        sorted_v = sort_model_info(v, sort_type)
        list_results.append({k: sorted_v})
    return list_results

@router.get('/get_model_by_local_path')
async def get_model_by_local_path(local_path: str):
    return await ModelInfoTable.get_model_info_by_file_path(local_path)

class DownloadCivitAIModelReq(PydanticModel):
    civitai_model_version: CivitaiModelVersion
    files_to_download: list[CivitaiFileToDownload]
    image_to_download: Optional[str]

@router.get('/get_downloading_models')
async def get_downloading_models():
    return ModelDownloadInfoTable.get_all_downloading_records()

@router.post('/download_civitai_model')
async def download_civitai_model(req: DownloadCivitAIModelReq):
    civitai_model_version = req.civitai_model_version
    files_to_download = req.files_to_download
    image_to_download = req.image_to_download

    try:
        # download image first, all models use one image
        downloaded_image_path = await download_civitai_image_to_whatsai_file_dir(image_to_download)

        # download_civitai_image_to_whatsai_file_dir may fail.
        downloaded_image_path = downloaded_image_path if downloaded_image_path else image_to_download

        # it may partially fail, leave it to user to resubmit.
        for file_to_download in files_to_download:
            await _download_civitai_model(
                file_to_download,
                downloaded_image_path,
                civitai_model_version,
            )

    except Exception as e:
        logger.error(e)
        traceback.print_exc()
        return str(e)

async def _download_civitai_model(
        file_to_download: CivitaiFileToDownload,
        downloaded_image_path: str,
        civitai_model_version: CivitaiModelVersion,
):
    downloading_model_info, error_info = await file_to_download_2_model_download_info(
        file_to_download,
        civitai_model_version,
        downloaded_image_path
    )

    if error_info:
        logger.debug('_download_civitai_model error:', error_info)
        return

    if downloading_model_info:
        start_to_download(downloading_model_info)

downloading_threads = {}
def start_to_download(downloading_model_info: ModelDownloadingInfo):
    if not downloading_threads.get(downloading_model_info.url, None):
        t = threading.Thread(target=download_civitai_model_task, args=(downloading_model_info,))
        t.start()
        downloading_threads[downloading_model_info.url] = t
    return

class OtherUIReq(PydanticModel):
    ui_name: str
    ui_dir: str
    set_as_default: bool = False

@router.post('/model_dir/add_other_ui_model_paths')
async def add_other_ui_model_paths_(req: OtherUIReq):
    ui_name = req.ui_name
    ui_dir = req.ui_dir
    set_as_default = req.set_as_default

    """ Add Webui or ComfyUI model paths. """
    if ui_name.lower() == 'webui':
        added_paths, info = await ModelDirTable.add_webui_dirs(ui_dir, set_as_default)
    elif ui_name.lower() == 'comfyui':
        added_paths, info = await ModelDirTable.add_comfy_dirs(ui_dir, set_as_default)
    else:
        return {
            'added_paths': None,
            'info': "Only webui and comfyui supported yet."
        }
    return {
        'added_paths': added_paths,
        'info': info
    }

@router.get('/model_dir/get_other_ui_model_paths_map')
async def get_other_ui_model_paths_map(ui_name: str):
    if ui_name.lower() == 'webui':
        return webui_model_dirs_map
    elif ui_name.lower() == 'comfyui':
        return comfyui_model_dirs_map


@router.get('/model_dir/{model_type}')
async def model_dir(model_type: str):
    results = await ModelDirTable.get_single_model_dir_record(model_type)
    return fill_model_dir_record(results)

def fill_model_dir_record(results):
    if results and results['dirs']:
        default_dir = results['default_dir']
        dirs = results['dirs']
        dirs_with_count = []
        for _dir in dirs:
            count = len(ModelDirTable.sync_get_model_files_in_dir(_dir))
            if default_dir and _dir == default_dir:
                dirs_with_count.append({
                    'dir': _dir,
                    'model_count': count,
                    'is_default': True
                })
            else:
                dirs_with_count.append({
                    'dir': _dir,
                    'model_count': count,
                    'is_default': False
                })
        results['dirs'] = dirs_with_count
    return results

class AddModelDirRequest(PydanticModel):
    model_type: str
    model_dir: str
    register_model_type_if_not_exists: bool = False
    set_as_default: bool = False

@router.post('/model_dir/add_model_dir')
async def add_model_dir(req: AddModelDirRequest):
    model_type = req.model_type
    model_dir = req.model_dir
    register_model_type_if_not_exists = req.register_model_type_if_not_exists
    set_as_default = req.set_as_default

    success, error_info, record = await ModelDirTable.add_model_dir(
        model_type,
        model_dir,
        register_model_type_if_not_exists,
        set_as_default,
    )
    if success:
        filled_record = fill_model_dir_record(record)

        return {
            'success': success,
            'error_info': error_info,
            'record': filled_record
        }
    else:
        return{
            'success': success,
            'error_info': error_info,
            'record': record
        }

class RemoveModelDirRequest(PydanticModel):
    model_type: str
    model_dir: str

@router.post('/model_dir/remove_model_dir')
async def remove_model_dir(req: RemoveModelDirRequest):
    model_type = req.model_type
    model_dir = req.model_dir

    success, error_info, record = await ModelDirTable.remove_model_dir(
        model_type,
        model_dir,
    )
    if success:
        filled_record = fill_model_dir_record(record)

        return {
            'success': success,
            'error_info': error_info,
            'record': filled_record
        }
    else:
        return {
            'success': success,
            'error_info': error_info,
            'record': None
        }


class SetDefaultModelDirRequest(PydanticModel):
    model_type: str
    model_dir: str

@router.post('/model_dir/set_default_model_dir')
async def set_default_model_dir(req: SetDefaultModelDirRequest):
    model_type = req.model_type
    model_dir = req.model_dir

    success, error_info, record = await ModelDirTable.set_default_model_dir(
        model_type,
        model_dir,
    )
    #
    if success:
        filled_record = fill_model_dir_record(record)

        return {
            'success': success,
            'error_info': error_info,
            'record': filled_record
        }
    else:
        return {
            'success': success,
            'error_info': error_info,
            'record': None

        }




