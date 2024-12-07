from fastapi import APIRouter

from misc.helpers_civitai import (
    get_civitai_model_info_by_version_id,
    get_civitai_model_info_by_hash,
    get_civitai_model_info_by_model_id, parse_civitai_url, try_to_make_sure_first_image_is_real_image,
    make_file_model_type_right
)
from misc.json_cache import JsonCache

router = APIRouter()

@router.get('/get_model_version_by_version_id')
async def get_model_version_by_version_id(model_version_id: int):
    return await get_civitai_model_info_by_version_id(model_version_id)

@router.get('/get_model_version_by_hash')
async def get_model_version_by_hash(hash_str: str):
    return await get_civitai_model_info_by_hash(hash_str)

@router.get('/get_model_version_by_model_id')
async def get_model_version_by_model_id(model_id: int, return_model_version=False):
    return await get_civitai_model_info_by_model_id(model_id, return_model_version)

@router.get("/get_civitai_model_version_info_with_url/")
async def get_civitai_model_version_info_with_url(url_str, use_cache=True):
    use_cache = False if (use_cache == 'false' or use_cache == False or use_cache == 0) else True
    if not url_str:
        return {
            'model_version_info': None,
            'error': "url_str required."
        }
    if use_cache and JsonCache.get('get_civitai_model_version_info', url_str):
        return {
            'model_version_info': JsonCache.get('get_civitai_model_version_info', url_str),
            'error': None
        }

    model_id, model_version_id = parse_civitai_url(url_str)
    if not model_id:
        return {
            'model_version_info': None,
            'error': "No model id parsed."
        }

    if model_version_id:
        civit_model_version_info, error_info = await get_civitai_model_info_by_version_id(model_version_id)
    elif model_id:
        civit_model_version_info, error_info = await get_civitai_model_info_by_model_id(model_id, return_model_version=True)
    else:
        civit_model_version_info = None
        error_info = "No model version info found."

    if civit_model_version_info:
        await try_to_make_sure_first_image_is_real_image(civit_model_version_info)
        make_file_model_type_right(civit_model_version_info)

    JsonCache.add('get_civitai_model_version_info', url_str, civit_model_version_info, expire_time=60 * 60 * 24)

    return {
        'model_version_info': civit_model_version_info,
        'error': error_info
    }