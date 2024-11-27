import traceback
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from starlette.responses import FileResponse

import core.addons
from core.widgets import WIDGET_FUNCTION_MAP, list_vaes
from tiny_db.helpers import sort_model_info
from data_type.whatsai_prompt import Prompt
from tiny_db.task import TaskTable
from tiny_db.card_input_cache import CardCache
from tiny_db.card_info import CardModelTable
from tiny_db.input_file import InputFile
from tiny_db.artwork import ArtworkTable
from tiny_db.media_file import MediaFile
from tiny_db.model_info import ModelInfoTable
from misc.helpers import file_type_guess
from misc.logger import logger
from misc.prompt_worker import TaskQueue

router = APIRouter()

@router.get('/card/local_card_info/{card_name}')
async def local_card_info(card_name: str, use_cache=True):
    cache_record = get_card_info_cache(card_name)

    if use_cache and cache_record:
        card_info = cache_record.get('card_info', None)
    else:
        card_class = CardModelTable.get_card_class(card_name)
        if not card_class:
            return {
                'errorMessage': "Card: {} not found.".format(card_name),
                'cardInfo': None
            }
        card_info = card_class().card_info
    return {
        'errorMessage': None,
        'cardInfo': card_info
    }

@router.get('/card/card_inputs_info/{card_name}')
async def card_inputs_info(card_name: str):
    cache_record = get_card_info_cache(card_name)
    card_info = cache_record.get('card_info', None)

    if not card_info :
        return {
            'errorMessage': "Card: {} not found in cache.".format(card_name),
            'cardInputInfo': None
        }
    else:
        card_inputs_info = card_info_to_prompt(card_info)
        return {
            'errorMessage': None,
            'cardInputInfo': card_inputs_info
        }

@router.get('/card/sync_custom_cards')
def sync_custom_cards():
    return CardModelTable.sync_custom_cards()


@router.post('/card/cache_card_prompt')
def cache_card_prompt(req: CardCache.DataModel):
    card_info = req.card_info
    card_name = req.card_name

    if not card_info:
        CardCache.delete(card_name)
    else:
        try:
            CardCache.update_or_insert(card_name, card_info)
        except Exception as e:
            traceback.print_exc()
            CardCache.delete(card_name)
            return False
    return True

@router.get('/card/get_card_info_cache')
def get_card_info_cache(card_name: str):
    return CardCache.get(card_name)

def full_card_info(card, background_tasks: BackgroundTasks):
    pre_models = card.get('pre_models', [])
    is_ready = True
    for model_hash in pre_models:
        model_info = ModelInfoTable.sync_get_model_info_by_hash(model_hash)
        if not model_info:
            is_ready = False
    card['is_ready'] = is_ready

    cover_image = card.get('cover_image', None)
    if cover_image:
        local_image = MediaFile.get_by_url(cover_image)
        if local_image:
            card['cover_image'] = local_image.get('local_path', None)
        else:
            background_tasks.add_task(MediaFile.add_record, cover_image)

    return card

@router.get('/card/all_cards')
async def get_all_cards(background_tasks: BackgroundTasks):
    cards = await CardModelTable.get_all_cards(force_renew=True)
    full_cards = []
    for card in cards:
        full_card = full_card_info(card, background_tasks)
        full_cards.append(full_card)
    return full_cards

@router.get('/card/download_pre_models')
async def download_pre_models(card_name: str):
    pass

@router.get('/addon/addon_info/{addon_name}')
async def local_addon_info(addon_name: str):
    from core.abstracts import ADD_ON_CLASS_MAP
    addon_class = ADD_ON_CLASS_MAP.get(addon_name)
    if addon_class:
        return {
            'errorMessage': None,
            'addon_info': addon_class().addon_info
        }
    else:
        return {
            'errorMessage': "Addon: {} not found.".format(addon_class),
            'addon_info': None
        }

class GenerationReq(BaseModel):
    card_name: str
    client_id: str

@router.post('/generate')
async def generate(req: GenerationReq):
    card_name = req.card_name
    client_id = req.client_id
    card_info_resp = await local_card_info(card_name, use_cache=True)
    card_info = card_info_resp["cardInfo"]
    if not card_info:
        return card_info
    prompt = card_info_to_prompt(card_info)
    TaskQueue.put(prompt, client_id)
    return True

def card_info_to_prompt(card_info, filter_none=True):
    card_name = card_info["card_name"]
    widgets = card_info["widgets"]
    addons = card_info["addons"]

    def is_none_in_dict_values(d: dict):
        result = False
        for k, v in d.items():
            if v is None or v == 'None':
                result = True
                return result

    base_inputs = {}
    for widget in widgets:
        widget_type = widget.get('widget_type')
        if widget_type == 'GroupedWidgets':
            _widgets = widget.get('value')
            for _widget in _widgets:
                parma_name = _widget.get('param_name')
                value = _widget.get('value')
                base_inputs[parma_name] = value
        else:
            parma_name = widget.get('param_name')
            value = widget.get('value')
            base_inputs[parma_name] = value

    addon_inputs = {}
    for addon in addons:
        addon_name = addon.get('addon_name')
        addon_widgets_list = addon.get('widgets')
        can_turn_off = addon.get('can_turn_off')
        is_off = addon.get('is_off')

        if can_turn_off and is_off:
            continue

        addon_inputs_list = []
        for addon_widgets in addon_widgets_list:
            addon_widgets_input = {}
            for addon_widget in addon_widgets:
                parma_name = addon_widget.get('param_name')
                value = addon_widget.get('value')
                addon_widgets_input[parma_name] = value

            if filter_none and is_none_in_dict_values(addon_widgets_input):
                continue
            addon_inputs_list.append(addon_widgets_input)

        if addon_inputs_list:
            addon_inputs[addon_name] = addon_inputs_list

    prompt = Prompt(
        card_name=card_name,
        base_inputs=base_inputs,
        addon_inputs=addon_inputs
    )
    return prompt

class WidgetFunctionParams(BaseModel):
    func_name: str
    extra_params: Optional[dict]

@router.post('/list_models')
async def list_models(params: WidgetFunctionParams):
    func_name = params.func_name
    extra_params = params.extra_params
    function = WIDGET_FUNCTION_MAP.get(func_name)
    if not function:
        logger.debug('function not found, params: {}'.format(params))
        return None
    if extra_params:
        return sort_model_info(function(**extra_params))
    else:
        return sort_model_info(function())

@router.get('/list_vaes')
async def list_vae():
    return list_vaes()

@router.get('/local_file')
async def get_local_file(path: str):
    if not path:
        return None
    path = Path(path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    mime = file_type_guess(path)
    return FileResponse(path, media_type=mime)

@router.get('/art/search')
async def art_search(substr: str | None = None):
    return await ArtworkTable.search_by_substr(substr)

@router.get('/art/get_artworks')
async def get_artworks():
    return await ArtworkTable.get_artworks(None)

@router.get('/art/get_artwork')
async def get_artwork(artwork_id: int):
    return await ArtworkTable.get_artwork(artwork_id)

@router.get('/art/get_art_by_path')
async def get_art_by_path(path: str):
    return await ArtworkTable.get_art_by_path(path)

@router.get('/recently_used/')
async def recently_used(media_type: str, sub_key: str = ""):
    supported_media_type = ['image', 'audio', 'video']
    if media_type not in supported_media_type:
        return []
    return InputFile.get_input_files(media_type, sub_key)

class MediaAddRequest(BaseModel):
    media_type: str
    sub_key: Optional[str] = ""
    local_path: str

@router.post('/add_recently_used')
async def add_recently_used(req: MediaAddRequest):
    file = InputFile.add_input_file(file_path=req.local_path, sub_key=req.sub_key)
    return file

# @router.get('/test_multi_d')
# def test_multi_d():
#     from misc.pypi_multi_versoins import import_helper, Dependency
#     import tqdm
#     import scipy
#
#     print(tqdm.__version__, scipy.__version__)
#     with import_helper([
#         Dependency(package_name='scipy', version='1.4.0'),
#         Dependency(package_name='tqdm', version='4.50.1'),
#     ]):
#         import tqdm as other_tqdm
#         import scipy as scipy_v
#         print(other_tqdm.__version__,other_tqdm, scipy_v, scipy_v.__version__, )
#
#     print(tqdm.__version__, scipy.__version__)


@router.get('/task/get_tasks')
async def get_tasks():
    tasks = await TaskTable.get_tasks(None)
    return tasks[:30]

@router.get('/task/remove_task')
async def remove_task(task_id: str):
    if not task_id:
        return False
    await TaskTable.remove_task(int(task_id))
    return True

@router.get('/utils/is_dir_path_ok')
def is_dir_path_ok(dir_path: str):
    path = Path(dir_path)
    if not Path(path).exists():
        return "Path: '{}' not exists.".format(dir_path)
    if not path.is_dir():
        return False, "Path: '{}' must be dir to store model files.".format(dir_path)
    return 'ok'
