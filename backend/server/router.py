from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from starlette.responses import FileResponse

from core.widgets import WIDGET_FUNCTION_MAP, list_vaes
from data_type.whatsai_card import CardDataModel, download_cover_image, CardInfo
from data_type.helpers import sort_model_info
from data_type.whatsai_task import Task
from data_type.whatsai_input_file import InputFile
from data_type.whatsai_artwork import Artwork
from misc.helpers import file_type_guess
from misc.logger import logger
from prompt_worker import TaskQueue, PromptWorker

router = APIRouter()


@router.get('/card/local_card_info/{card_name}')
async def local_card_info(card_name: str, use_cache=True):
    # fill_default_card_infos when server starts, make sure it's done before info got.
    try:
        CardDataModel.fill_default_infos_of_card()
    except Exception as e:
        pass

    card_record = CardDataModel.get(card_name)
    if not card_record:
        return {
            'errorMessage': "Card: {} not found.".format(card_name),
            'cardInfo': None
        }

    return {
        'errorMessage': None,
        'cardInfo': card_record.get_card_info(use_cache)
    }


@router.get('/card/is_card_ready/{card_name}')
async def is_card_ready(card_name: str):
    card_record = CardDataModel.get(card_name)
    return card_record and card_record.is_ready()


@router.get('/card/card_inputs_info/{card_name}')
async def card_inputs_info(card_name: str, use_cache=True):
    card_record = CardDataModel.get(card_name)

    if not card_record:
        return {
            'errorMessage': "Card: {} not found in cache.".format(card_name),
            'cardInputInfo': None
        }
    else:
        return {
            'errorMessage': None,
            'cardInputInfo': card_record.get_card_info(use_cache).to_prompt()
        }


@router.get('/card/sync_custom_cards')
def sync_custom_cards():
    return CardDataModel.sync_custom_cards()


class CacheCardPromptRequest(BaseModel):
    card_name: str
    card_info: dict | None


@router.post('/card/cache_card_prompt')
def cache_card_prompt(req: CacheCardPromptRequest):
    card_info = req.card_info
    card_name = req.card_name
    card_record = CardDataModel.get(card_name)
    if not card_record:
        return {
            'errorMessage': "Card: {} not found.".format(card_name),
            'cardInfo': None
        }
    if not card_info:  # clear cache
        card_record.cached_card_info = None
        card_record.save()
        return {
            'errorMessage': None,
            'cardInfo': card_record.default_card_info
        }
    else:
        card_record.cached_card_info = CardInfo(**card_info)
        card_record.save()
        return {
            'errorMessage': None,
            'cardInfo': card_record.cached_card_info
        }


@router.get('/card/all_cards')
async def get_all_cards(background_task: BackgroundTasks):
    all_cards = CardDataModel.get_all()
    for card in all_cards:
        if card and card.cover_image.startswith('http'):
            background_task.add_task(download_cover_image, card)
    return all_cards


@router.get('/card/download_pre_models')
async def download_pre_models(card_name: str):
    pass


@router.get('/addon/addon_info/{addon_name}')
async def local_addon_info(addon_name: str):
    from core.addons import ADD_ON_CLASS_MAP
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
    card_record = CardDataModel.get(card_name)
    if not card_record:
        return False

    current_card_info = card_record.get_card_info()
    prompt = current_card_info.to_prompt()
    TaskQueue.put(card_name, prompt, client_id)
    return True


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
    return Artwork.search_by_substr(substr)


@router.get('/art/get_artworks')
async def get_artworks(page_size: int = 20, page_num: int = 0):
    artworks = Artwork.get_all(limit=page_size, skip=page_size * page_num)
    has_next = len(artworks) == page_size
    return {
        'artworks': artworks,
        'page_num': page_num,
        'has_next': has_next
    }


@router.get('/art/get_artwork')
async def get_artwork(artwork_id: int):
    return Artwork.get(artwork_id)


@router.get('/art/get_art_by_path')
async def get_art_by_path(path: str):
    return Artwork.get(path)


@router.get('/recently_used/')
async def recently_used(media_type: str, sub_key: str = ""):
    supported_media_type = ['image', 'audio', 'video']
    if media_type not in supported_media_type:
        return []
    return InputFile.get_input_files(media_type, sub_key)


class MediaRequest(BaseModel):
    media_type: str
    sub_key: Optional[str] = ""
    local_path: str


@router.post('/add_recently_used')
async def add_recently_used(req: MediaRequest):
    try:
        file = InputFile.add_input_file(file_path=req.local_path, sub_key=req.sub_key)
        return file
    except Exception as e:
        logger.error(e)
        return None


@router.post('/remove_recently_used')
async def remove_recently_used(req: MediaRequest):
    try:
        media_files = InputFile.remove_and_return(
            file_path=req.local_path,
            media_type=req.media_type,
            sub_key=req.sub_key
        )
        return media_files
    except Exception as e:
        logger.error(e)
        return []


@router.get('/task/get_tasks')
async def get_tasks():
    tasks = Task.get_all()
    return tasks


@router.get('/task/remove_task')
async def remove_task(task_id: str):
    if not task_id:
        return False
    Task.remove(task_id)
    return True


@router.get('/utils/is_dir_path_ok')
def is_dir_path_ok(dir_path: str):
    path = Path(dir_path)
    if not Path(path).exists():
        return "Path: '{}' not exists.".format(dir_path)
    if not path.is_dir():
        return False, "Path: '{}' must be dir to store model files.".format(dir_path)
    return 'ok'


@router.get('/test/other_test')
async def other_test():
    from misc.helpers_civitai import sync_get_civitai_model_info_by_hash
    success, resp, error = sync_get_civitai_model_info_by_hash(
        'b87f0c1c541e30f6b507795ef3aa9f7e5a1726af566f8970b07ed717c13ec5a5')
    print(success, resp, error)
