from typing import Optional
from fastapi import APIRouter

from data_type.civitai_model_version import CivitaiModelVersion, CivitaiFileToDownload
from data_type.whatsai_model_download_task import ModelDownloadTask
from data_type.whatsai_model_info import ModelInfo
from misc.constants import webui_model_dirs_map, comfyui_model_dirs_map
from misc.helpers import (
    get_model_files_in_dir
)
from model_download_worker import submit_model_info_sync_task, submit_model_download_task
from data_type.helpers import sort_model_info, SortType
from data_type.whatsai_model_dir import ModelDir
from data_type.whatsai_model_type import ModelType
from data_type.base import PydanticModel
from misc.helpers_civitai import download_civitai_image_to_whatsai_file_dir

router = APIRouter()


@router.get('/get_all_model_types')
async def get_all_model_types():
    return ModelType.get_all_model_types()


@router.get('/model_infos_by_type')
async def model_infos_by_type(
        model_type: str | None = None,
        sort_type: SortType = 'created_reverse',
        base_model_filter: str | None = None
):
    """ Get model infos by type, used by frontend to select. If no model_type, all models will be return. """
    if not model_type:
        return ModelInfo.get_all()
    return ModelInfo.get_model_infos(model_type=model_type)


class SyncModelInfosReq(PydanticModel):
    model_type: Optional[str] = None


@router.post('/sync_model_infos')
async def sync_model_infos(req: SyncModelInfosReq):
    """ Sync model infos by type, if no model_type, all model infos will sync.
        We need it when user first setup or he/she put file in some dir manually.
    """
    model_type = req.model_type.lower()
    model_infos = ModelInfo.get_model_infos(model_type)
    for model_info in model_infos:
        submit_model_info_sync_task(model_info)
    return model_infos


class SyncSingeModelInfoReq(PydanticModel):
    model_file_path: str


@router.post('/sync_single_model_info')
async def sync_single_model_info(req: SyncSingeModelInfoReq):
    model_file_path = req.model_file_path
    model_info = ModelInfo.get(model_file_path)
    if model_info:
        submit_model_info_sync_task(model_info)


@router.get('/get_all_models')
async def get_all_models(sort_type: SortType = 'created_reverse'):
    """ Get all models in tiny db, rearrange them in type of:
        { 'model_type': [model_info_1, model_info_1 ... ]
    """
    model_infos = ModelInfo.get_all()
    model_types = ModelType.get_all_model_types()
    models_by_type_dict = {model_type: [] for model_type in model_types}

    for model_info in model_infos:
        model_type = model_info.model_type
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


@router.get('/get_model_by_model_id')
async def get_model_by_local_path(model_id: str):
    return ModelInfo.get(model_id, with_civitai_model_info=True)


@router.get('/get_model_by_local_path')
async def get_model_by_local_path(local_path: str):
    return ModelInfo.get(local_path, with_civitai_model_info=True)


class DownloadCivitAIModelReq(PydanticModel):
    civitai_model_version: CivitaiModelVersion
    files_to_download: list[CivitaiFileToDownload]
    image_to_download: Optional[str]


@router.get('/get_downloading_models')
async def get_downloading_models():
    return ModelDownloadTask.get_downloading_model_info_tasks()


@router.get('/cancel_downloading_task')
async def cancel_downloading_task(task_id: str):
    return ModelDownloadTask.cancel_task(task_id=task_id)


@router.post('/download_civitai_model')
async def download_civitai_model(req: DownloadCivitAIModelReq):
    civitai_model_version = req.civitai_model_version
    files_to_download = req.files_to_download
    image_to_download = req.image_to_download

    civitai_model_version.save()

    # download image first, all models use one image, it may fail.
    downloaded_image_path = await download_civitai_image_to_whatsai_file_dir(image_to_download)
    downloaded_image_path = downloaded_image_path if downloaded_image_path else image_to_download

    submit_model_download_task(civitai_model_version, files_to_download, downloaded_image_path)


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
        added_paths, info = ModelDir.add_webui_dirs(ui_dir, set_as_default)
    elif ui_name.lower() == 'comfyui':
        added_paths, info = ModelDir.add_comfy_dirs(ui_dir, set_as_default)
    else:
        return {
            'added_paths': None,
            'info': "Only webui and comfyui supported yet."
        }

    for added_path in added_paths:
        model_type, model_dir = added_path
        add_model_infos_in_dir(model_type, model_dir)

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
    return ModelDir.get(model_type)


class AddModelDirRequest(PydanticModel):
    model_type: str
    model_dir: str
    set_as_default: bool = False


@router.post('/model_dir/add_model_dir')
async def add_model_dir(req: AddModelDirRequest):
    model_type = req.model_type
    model_dir = req.model_dir
    set_as_default = req.set_as_default

    success, error_info, model_dir_obj = ModelDir.add_model_dir(
        model_type,
        model_dir,
        set_as_default,
    )

    if success and model_dir_obj:
        add_model_infos_in_dir(model_type, model_dir)

    return {
        'success': success,
        'error_info': error_info,
        'record': model_dir_obj
    }


def add_model_infos_in_dir(model_type, model_dir):
    model_files_in_dir = get_model_files_in_dir(model_dir)
    ModelInfo.add_with_many_local_paths(model_files_in_dir, model_type)
    model_infos_to_sync = ModelInfo.get_with_local_paths(model_files_in_dir)
    for model_info in model_infos_to_sync:
        submit_model_info_sync_task(model_info)


class RemoveModelDirRequest(PydanticModel):
    model_type: str
    model_dir: str


@router.post('/model_dir/remove_model_dir')
async def remove_model_dir(req: RemoveModelDirRequest):
    model_type = req.model_type
    model_dir = req.model_dir

    success, error_info, record = ModelDir.remove_model_dir(
        model_type,
        model_dir,
    )
    if success:
        ModelInfo.remove_models_in_dir(model_dir)

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

    success, error_info, record = ModelDir.set_default_model_dir(
        model_type,
        model_dir,
    )

    return {
        'success': success,
        'error_info': error_info,
        'record': record
    }
