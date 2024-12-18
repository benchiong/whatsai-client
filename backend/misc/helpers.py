import asyncio
import hashlib
import io
import os
import time
import traceback
import urllib.parse
from io import BytesIO
from pathlib import Path
from datetime import datetime

import aiofiles
import httpx
import requests
from PIL import Image, ImageFile, UnidentifiedImageError

from filetype import filetype

from misc.constants import supported_pt_extensions
from misc.json_cache import JsonCache
from misc.logger import logger
from misc.whatsai_dirs import cache_dir

datetime_formatter = '%Y-%m-%d %H:%M:%S'


async def async_get(url, headers=None, timeout=10, retry=3):
    while retry > 0:
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                return await client.get(url, headers=headers)
        except Exception as e:
            await asyncio.sleep(3)
            retry -= 1
            logger.debug(f"async_get error: {e}")
            traceback.print_exc()
    return None


def sync_get(url, headers=None, timeout=10, retry=3):
    while retry > 0:
        try:
            return requests.get(url, headers=headers, timeout=timeout)
        except Exception as e:
            time.sleep(3)
            retry -= 1
            logger.debug(f"sync_get error: {e}")
            traceback.print_exc()
    return None


async def async_post(url, data, headers=None, timeout=10, retry=3):
    while retry > 0:
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                return await client.post(url, data=data, headers=headers)
        except Exception as e:
            await asyncio.sleep(3)
            retry -= 1
            logger.debug(f"async_post error: {e}")
            traceback.print_exc()


def sync_post(url, data, headers=None, timeout=10, retry=3):
    while retry > 0:
        try:
            return requests.post(url, data=data, headers=headers, timeout=timeout)
        except Exception as e:
            time.sleep(3)
            retry -= 1
            logger.debug(f"sync_post error: {e}")
            traceback.print_exc()


async def async_head(url, headers=None, timeout=10):
    retry = 3
    while retry > 0:
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                return await client.head(url, headers=headers)
        except Exception as e:
            await asyncio.sleep(3)
            retry -= 1
            logger.debug(f"async_head error: {e}")
    return None


def sync_head(url, headers=None, timeout=10):
    retry = 3
    while retry > 0:
        try:
            return requests.head(url, headers=headers, timeout=timeout)
        except Exception as e:
            time.sleep(3)
            retry -= 1
            logger.debug(f"sync_head error: {e}")
    return None


async def download_image(url: str, file_path: str, headers=None):
    try:
        local_image_path = JsonCache.get('download_image', url)
        if not local_image_path or not Path(local_image_path).exists():
            resp = await async_get(url, headers)

            if resp and resp.content:
                image = Image.open(BytesIO(resp.content)).convert('RGB')
                image.save(file_path)
                JsonCache.add('download_image', url, file_path)
                return file_path
            else:
                return None
        else:
            return local_image_path
    except Exception as e:
        traceback.print_exc()
        return None


def sync_download_image(url: str, file_path: str, headers=None):
    try:
        local_image_path = JsonCache.get('download_image', url)
        if not local_image_path or not Path(local_image_path).exists():
            resp = sync_get(url, headers=None)
            if resp and resp.content:
                image = Image.open(BytesIO(resp.content)).convert('RGB')
                image.save(file_path)
                JsonCache.add('download_image', url, file_path)
                return file_path
            else:
                return None
        else:
            return local_image_path
    except Exception as e:
        traceback.print_exc()
        return None


def get_file_created_timestamp_and_datetime(file_path: str):
    if not Path(file_path).exists():
        return None, None
    global datetime_formatter
    stamp = int(os.path.getctime(file_path))
    date_str = datetime.fromtimestamp(stamp).strftime(datetime_formatter)
    return stamp, date_str


def get_file_size_in_kb(file_path: str):
    if not Path(file_path).exists():
        return None

    return os.path.getsize(file_path) / 1024


def get_files_in_dir(dir_path: str | Path):
    """ Get all files in the dir path. """
    files = []
    dir_path = Path(dir_path) if isinstance(dir_path, str) else dir_path

    if not dir_path.exists() or not dir_path.is_dir():
        return []

    for child in dir_path.iterdir():
        if child.is_file():
            files.append(child)
        elif child.is_dir():
            sub_files = get_files_in_dir(child)
            files.extend(sub_files)
        else:
            # Do we need to deal with others here? mount/symlink etc.
            pass
    return files


def get_model_files_in_dir(dir_path: str):
    files_in_dir = get_files_in_dir(dir_path)

    model_files = []
    for file in files_in_dir:  # filter by suffix and file name.
        name = file.name
        ext = file.suffix
        if not name.startswith(('.', '_')) and ext in supported_pt_extensions:
            model_files.append(str(file.absolute()))

    return model_files


def get_items_in_dir(dir_path: str | Path):
    dir_path = Path(dir_path) if isinstance(dir_path, str) else dir_path

    if not dir_path.exists() or not dir_path.is_dir():
        return []

    r = []
    for p in dir_path.iterdir():
        if '__pycache__' not in p.__str__():
            r.append(p)
    return r


async def read_chunks(file, size: int = io.DEFAULT_BUFFER_SIZE):
    """Yield pieces of data from a file-like object until EOF."""
    while True:
        chunk = await file.read(size)
        if not chunk:
            break
        yield chunk


def sync_read_chunks(file, size: int):
    while chunk := file.read(size):
        if not chunk:
            break
        yield chunk


async def gen_file_sha256(file_path: str):
    cache_key = 'file_sha256'
    hash_str = JsonCache.get(cache_key, file_path)
    if hash_str:
        return hash_str

    block_size = 1 << 20
    h = hashlib.sha256()
    length = 0
    async with aiofiles.open(file_path, mode='rb') as f:
        async for block in read_chunks(f, size=block_size):
            length += len(block)
            h.update(block)

    hash_value = h.hexdigest()
    JsonCache.add(cache_key, file_path, hash_value)
    return hash_value


def sync_gen_file_sha256(file_path: str) -> str:
    cache_key = 'file_sha256'
    hash_str = JsonCache.get(cache_key, file_path)
    if hash_str:
        return hash_str

    block_size = 1 << 20
    h = hashlib.sha256()
    length = 0

    with open(file_path, mode='rb') as f:
        for block in sync_read_chunks(f, size=block_size):
            length += len(block)
            h.update(block)

    hash_value = h.hexdigest()
    JsonCache.add(cache_key, file_path, hash_value)
    return hash_value


def thumbnail(file_path: str, max_edge=256, min_size=64):
    # todo: deal with other file types
    path = Path(file_path)
    if not path.exists():
        return None, None
    if path.stat().st_size < min_size * 1024:
        return file_path, None

    thumb_file_path = str(cache_dir / Path(file_path).stem) + '.webp'
    with Image.open(path) as img:
        img.thumbnail((max_edge, max_edge))
        img.save(thumb_file_path, "webp")

    return thumb_file_path, img.size


def file_type_guess(file):
    kind = filetype.guess(file)
    return kind.mime if kind else None


def is_url(may_be_url: str):
    try:
        result = urllib.parse.urlparse(may_be_url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


# from ComfyUI
def pillow(fn, arg):
    prev_value = None
    try:
        x = fn(arg)
    except (OSError, UnidentifiedImageError, ValueError):  # PIL issues #4472 and #2445, also fixes ComfyUI issue #3416
        prev_value = ImageFile.LOAD_TRUNCATED_IMAGES
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        x = fn(arg)
    finally:
        if prev_value is not None:
            ImageFile.LOAD_TRUNCATED_IMAGES = prev_value
    return x

def get_meta_info(file_path):
    # todo, support video/ audio ...
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            image_format = img.format
            return {
                'width': width,
                'height': height,
                'format': image_format
            }
    except Exception as e:
        logger.debug(e)
        traceback.print_exc()
        return {}



def get_now_timestamp_and_str():
    now = datetime.now()
    timestamp = int(now.timestamp())
    datetime_str = now.strftime("%Y/%m/%d %H:%M:%S")
    return timestamp, datetime_str
