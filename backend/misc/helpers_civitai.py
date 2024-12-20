import os
import re
import time
import traceback
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import requests
import urllib3

from data_type.whatsai_model_download_task import ModelDownloadTask, TaskStatus

#  https://python-forum.io/thread-36981.html
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from data_type.civitai_model_version import CivitaiFileToDownload, CivitaiModelVersion
from data_type.whatsai_model_downloading_info import ModelDownloadingInfo
from misc.helpers import async_get, gen_file_sha256, async_head, download_image, \
    get_file_created_timestamp_and_datetime, get_file_size_in_kb, sync_get, sync_head, sync_download_image
from misc.json_cache import JsonCache
from misc.logger import logger
from misc.whatsai_dirs import model_info_images_dir
from data_type.whatsai_model_dir import ModelDir
from data_type.whatsai_model_info import ModelInfo

# Mostly from: https://github.com/butaixianran/Stable-Diffusion-Webui-Civitai-Helper, thanks.

# civitai urls:
# https://civitai.com/api/v1/model-versions/by-hash/A5E5A941A3217247DBCECEEE5B67F8D6B1EF2514260E08A5757436BEC7035F93
# https://civitai.com/api/v1/models/7240
# https://civitai.com/api/v1/model-versions/948574


civitai_url_dict = {
    "modelPage": "https://civitai.com/models/",
    "modelId": "https://civitai.com/api/v1/models/",
    "modelVersionId": "https://civitai.com/api/v1/model-versions/",
    "hash": "https://civitai.com/api/v1/model-versions/by-hash/"
}

def_headers_to_request_civitai = {
    'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    "Authorization": "Bearer 916ef340507f01e5a02bf66b1841cb2f"  # todo: add Authorization logic
}


async def get_civitai_model_info_by_hash(hash_str: str):
    if not hash_str:
        return False, None, "Hash_str is required."

    url = civitai_url_dict["hash"] + hash_str
    try:
        cached_result = JsonCache.get("get_civitai_model_info_by_hash", hash_str)
        if cached_result:
            return True, cached_result, None

        resp = await async_get(url, headers=def_headers_to_request_civitai)
        if resp is None:
            return False, None, "get_civitai_model_info_by_hash async_get error, hash: {}".format(hash_str)

        if resp.status_code == 404:
            return False, None, "Model version info not found on civitai, the hash_str id: {}".format(hash_str)

        resp_content = resp.json()
        JsonCache.add("get_civitai_model_info_by_hash", hash_str, resp_content)
        return True, resp_content, None
    except Exception as e:
        logger.debug("get_civitai_model_info_by_hash error:", e)
        traceback.print_exc()
        return False, None, str(e)


def sync_get_civitai_model_info_by_hash(hash_str: str):
    if not hash_str:
        return False, None, "Hash_str is required."

    url = civitai_url_dict["hash"] + hash_str
    try:
        cached_result = JsonCache.get("get_civitai_model_info_by_hash", hash_str)
        if cached_result:
            return True, cached_result, None

        resp = sync_get(url, headers=def_headers_to_request_civitai)

        if resp is None:
            return False, None, "get_civitai_model_info_by_hash error, hash: {}".format(hash_str)

        if resp.status_code == 404:
            return True, None, "Model version info not found on civitai, the hash_str id: {}".format(hash_str)

        resp_content = resp.json()
        JsonCache.add("get_civitai_model_info_by_hash", hash_str, resp_content)
        return True, resp_content, None
    except Exception as e:
        logger.debug("get_civitai_model_info_by_hash error:", e)
        traceback.print_exc()
        return False, None, str(e)


async def get_civitai_model_info_by_model_id(model_id: int, return_model_version=False):
    if not model_id:
        return None, "Model_id is required."

    url = civitai_url_dict["modelId"] + str(model_id)
    try:
        resp = await async_get(url, headers=def_headers_to_request_civitai)

        if not resp:
            return None, "async_get error, model id: {}".format(model_id)

        if resp.status_code == 404:
            return None, "Model info not found on civitai, the model_id id: {}".format(model_id)

        resp_content = resp.json()
        if return_model_version:
            # take first version as default to return and complete model info
            model_version_list = resp_content.get('modelVersions')
            if model_version_list:
                model_version = model_version_list[0]
                model_version['model'] = {
                    'name': resp_content.get('name'),
                    'type': resp_content.get('type')
                }
                return model_version, None
            else:
                return None, "Model version info not found on civitai, the model_id id: {}".format(model_id)
        else:
            return resp_content, None
    except Exception as e:
        return None, str(e)


async def get_civitai_model_info_by_version_id(model_version_id: int):
    if not model_version_id:
        return None, "Model_version_id is required."

    url = civitai_url_dict["modelVersionId"] + str(model_version_id)
    try:
        resp = await async_get(url, headers=def_headers_to_request_civitai)
        if not resp:
            return None, "async_get error, model_version_id: {}".format(model_version_id)
        if resp.status_code == 404:
            return None, "Model version info not found on civitai, the version id: {}".format(model_version_id)
        resp_content = resp.json()
        return resp_content, None
    except Exception as e:
        return None, str(e)


async def get_civitai_model_info_by_local_file_hash(file_path: str):
    hash_str = await gen_file_sha256(file_path)
    civitai_model_info, _ = await get_civitai_model_info_by_hash(hash_str)
    return civitai_model_info


async def is_content_type_image(url):
    cached_result = JsonCache.get('is_content_type_image', url)
    if not cached_result:
        resp = await async_head(url, headers=def_headers_to_request_civitai)
        if not resp:
            return False

        content_type = None
        if resp.headers and resp.headers.get('content-type'):
            content_type = resp.headers.get('content-type')

        JsonCache.add('is_content_type_image', url, content_type)
    else:
        content_type = cached_result

    return content_type and 'image' in content_type


def sync_is_content_type_image(url):
    cached_result = JsonCache.get('is_content_type_image', url)
    if not cached_result:
        resp = sync_head(url, headers=def_headers_to_request_civitai)
        if not resp:
            return False

        content_type = None
        if resp.headers and resp.headers.get('content-type'):
            content_type = resp.headers.get('content-type')

        JsonCache.add('is_content_type_image', url, content_type)
    else:
        content_type = cached_result

    return content_type and 'image' in content_type


async def get_real_image_info(image_infos: list[dict]):
    """ Image urls return by civitai sometime are videos with extension: .jpeg
        e.g. https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/91c92a29-7ae7-4ad1-b52d-956ded23d410/width=450/14107615.jpeg
        model case: https://civitai.com/models/486271?modelVersionId=540748
    """

    first_img_info = None
    for index, image_info in enumerate(image_infos):
        url = image_info.get('url')
        if index == 0 and url:
            # return a data anyway?
            first_img_info = first_img_info
        try:
            is_image = await is_content_type_image(url)
            if is_image:
                return image_info
        except Exception as e:
            traceback.print_exc()
            logger.error(e)
            continue
    return first_img_info


def sync_get_real_image_info(image_infos: list[dict]):
    """ sync version of get_real_image_info """

    first_img_info = None
    for index, image_info in enumerate(image_infos):
        url = image_info.get('url')
        if index == 0 and url:
            first_img_info = first_img_info
        try:
            is_image = sync_is_content_type_image(url)
            if is_image:
                return image_info
        except Exception as e:
            traceback.print_exc()
            logger.error(e)
            continue
    return first_img_info


async def get_image_url_of_civitai_model_info(civitai_model_info: dict):
    image_infos = civitai_model_info.get('images')
    if not image_infos:
        return None

    image_info = await get_real_image_info(image_infos)
    if not image_info:
        return None

    return image_info.get('url')


def sync_get_image_url_of_civitai_model_info(civitai_model_info: dict):
    image_infos = civitai_model_info.get('images')
    if not image_infos:
        return None

    image_info = sync_get_real_image_info(image_infos)
    if not image_info:
        return None

    return image_info.get('url')


async def try_to_make_sure_first_image_is_real_image(civit_model_version_info: dict | None):
    if not civit_model_version_info:
        return

    images = civit_model_version_info.get('images', [])
    if not images:
        return

    image_info_with_maybe_real_image = await get_real_image_info(images)

    images[0] = image_info_with_maybe_real_image
    civit_model_version_info['images'] = images


def sync_try_to_make_sure_first_image_is_real_image(civit_model_version_info: dict | None):
    if not civit_model_version_info:
        return

    images = civit_model_version_info.get('images', [])
    if not images:
        return

    image_info_with_maybe_real_image = get_real_image_info(images)

    images[0] = image_info_with_maybe_real_image
    civit_model_version_info['images'] = images


def make_file_model_type_right(civit_model_version_info: dict | None):
    """ CivitAI leave the primary file's type: Model, fix it here.
        todo: make sure it is work for sufficient cases.
    """
    if not civit_model_version_info:
        return
    files = civit_model_version_info.get('files', [])
    if not files:
        return

    model_type = civit_model_version_info.get('model', {}).get('type')
    if not model_type:
        return

    for index, file in enumerate(files):
        if file['type'] == 'Model':
            file['type'] = model_type
            files[index] = file

    civit_model_version_info['files'] = files


def civitai_url(model_id, version_id):
    if not model_id:
        return None

    url = 'https://civitai.com/models/' + str(model_id)
    if version_id:
        url += '?modelVersionId=' + str(version_id)
    return url


def parse_civitai_url(url: str) -> (int, int):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    model_id_match = re.search(r"/models/(\d+)", url)
    model_id = int(model_id_match.group(1)) if model_id_match else None
    model_version_id = int(query_params.get('modelVersionId', [0])[0])
    model_version_id = model_version_id if model_version_id else None
    return model_id, model_version_id


def file_to_download_2_model_download_info(
        file_to_download: CivitaiFileToDownload,
        model_version: CivitaiModelVersion,
        downloaded_image_path: str
):
    file_name = file_to_download.civitaiFile.name
    sha_256 = file_to_download.civitaiFile.hashes.SHA256

    model_type = file_to_download.modelType
    size_kb = file_to_download.civitaiFile.sizeKB
    civit_model = model_version

    dir_obj = ModelDir.get(model_type)
    if not dir_obj:
        return None, "Dir record not found."

    dir_path = dir_obj.default_dir
    if not dir_path:
        return None, "Dir to download not found."

    local_path = Path(dir_path) / file_name
    download_url = file_to_download.civitaiFile.downloadUrl

    model_info = ModelInfo(
        local_path=str(local_path),
        file_name=file_name,
        sha_256=sha_256,
        model_type=model_type,
        image_path=downloaded_image_path,
        civit_model_version_id=civit_model.id,
        civit_model=civit_model,
        size_kb=size_kb,
        dir=str(local_path.parent),
        base_model=civit_model.baseModel,
        civit_info_synced=True,
        download_url=download_url
    )

    model_downloading_info = ModelDownloadingInfo(
        url=download_url,
        total_size=file_to_download.civitaiFile.sizeKB,
        model_info=model_info,
        downloaded_size=0.0,
        downloaded_time=0.0,
        progress=0.0
    )

    return model_downloading_info, None


def download_civitai_model_task(download_model_info: ModelDownloadingInfo):
    while True:
        try:
            local_model_path = download_civitai_model_worker(download_model_info)
            if local_model_path:
                logger.debug(f"model downloaded: {local_model_path}")
                download_model_info.finished = True
                download_model_info.save()
                return
        except Exception as e:
            traceback.print_exc()
            logger.debug(e)


def download_civitai_model_worker(model_downloading_info: ModelDownloadingInfo, task: ModelDownloadTask):
    """ Mostly from:
    https://github.com/butaixianran/Stable-Diffusion-Webui-Civitai-Helper/blob/main/scripts/ch_lib/downloader.py#L14
    thanks.
    """

    local_path = model_downloading_info.model_info.local_path
    downloading_path = model_downloading_info.downloading_file()
    url_to_download = model_downloading_info.url

    # we have unfinished task
    if os.path.exists(downloading_path):
        downloaded_size = os.path.getsize(downloading_path)

        # if we have download record in db, they have same local_path, recover its download progress info,
        # Add a new record otherwise.
        origin_download_model_info = ModelDownloadingInfo.get(url_to_download)
        if origin_download_model_info and origin_download_model_info.model_info.local_path == local_path:
            model_downloading_info = origin_download_model_info
        else:
            model_downloading_info.save()
    else:
        model_downloading_info.save()
        downloaded_size = 0

    # create header range
    headers = {
        **def_headers_to_request_civitai,
        'Range': 'bytes=%d-' % downloaded_size,
    }

    # download process
    time_start = time.time()  # record begin time before request
    consumed_downloaded_time = model_downloading_info.downloaded_time  # record last download consumed time

    resp = requests.get(url_to_download, stream=True, verify=False, headers=headers)
    with open(downloading_path, "ab") as f:
        size_to_update = 1024 * 512  # 512kB
        tmp_downloaded_size = 0
        for chunk in resp.iter_content(chunk_size=1024):
            if chunk:
                downloaded_size += len(chunk)
                tmp_downloaded_size += len(chunk)
                f.write(chunk)
                f.flush()

            # update record to tell frontend
            if tmp_downloaded_size > size_to_update:
                update_downloading_record(
                    model_downloading_info,
                    consumed_downloaded_time,
                    time_start,
                    downloaded_size / 1024,
                    task
                )
                tmp_downloaded_size = 0

            task_canceled = ModelDownloadTask.get(task.id).task_status == TaskStatus.canceled.value
            if task_canceled:
                logger.debug(f"task canceled {task.id}")
                return False, None

    # finish downloading
    os.rename(downloading_path, local_path)

    # update model info and save
    model_info = model_downloading_info.model_info

    time_stamp, datetime_str = get_file_created_timestamp_and_datetime(model_info.local_path)
    size_kb = get_file_size_in_kb(model_info.local_path)

    model_info.size_kb = size_kb
    model_info.created_time_stamp = time_stamp
    model_info.created_datetime_str = datetime_str
    model_info.save()

    # update model download info
    model_downloading_info.finished = True
    model_downloading_info.eta = 0.0
    model_downloading_info.progress = 1.0
    model_downloading_info.downloaded_size = size_kb
    model_downloading_info.save()

    return True, local_path


def update_downloading_record(
        download_model_info: ModelDownloadingInfo,
        origin_downloaded_time: float,
        time_start: float,
        downloaded_size: float,
        task: ModelDownloadTask
):
    total_size = download_model_info.total_size

    # calculate total download time in case the download restarted.
    time_consumed = time.time() - time_start
    downloaded_time = origin_downloaded_time + time_consumed

    # update related fields
    download_model_info.downloaded_time = downloaded_time
    download_model_info.downloaded_size = downloaded_size

    # to avoid divided by zero
    const_num = 1e-15

    # calculate progress
    progress = min((downloaded_size * 1.0) / (total_size * 1.0 + const_num), 1.0)
    download_model_info.progress = progress

    # calculate eta
    eta = downloaded_time / (progress + const_num) - downloaded_time
    download_model_info.eta = eta

    # update the record
    task.workload = download_model_info
    download_model_info.save()
    task.save()


async def download_civitai_image_to_whatsai_file_dir(url: str):
    if not url:
        return None

    file_name = Path(url).name
    local_image_path = model_info_images_dir / file_name
    success = await download_image(url, local_image_path.__str__(), headers=def_headers_to_request_civitai)
    return local_image_path.__str__() if success else None


def sync_download_civitai_image_to_whatsai_file_dir(url: str):
    if not url:
        return None

    file_name = Path(url).name
    local_image_path = model_info_images_dir / file_name
    success = sync_download_image(url, local_image_path.__str__(), headers=def_headers_to_request_civitai)
    return local_image_path.__str__() if success else None
