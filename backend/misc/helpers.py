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

from misc.json_cache import JsonCache
from misc.logger import logger

datetime_formatter = '%Y-%m-%d %H:%M:%S'
async def async_get(url, headers=None, timeout=10, retry=3):
    while retry > 0:
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                return await client.get(url, headers=headers)
        except Exception as e:
            time.sleep(3)
            retry -= 1
            logger.debug("async_get error")
            traceback.print_exc()
    return None

async def async_post(url, headers=None, timeout=10, retry=3):
    while retry > 0:
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                return await client.post(url, headers=headers)
        except Exception as e:
            time.sleep(3)
            retry -= 1
            logger.debug("async_post error")
            traceback.print_exc()

async def async_head(url, headers=None, timeout=10):
    retry = 3
    while retry > 0:
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                return await client.head(url, headers=headers)
        except Exception as e:
            time.sleep(3)
            retry -= 1
            logger.debug("async_head error")
    return None


async def download_image(url: str, file_path: str, headers=None):
    cached_image = JsonCache.get('download_image', url)
    if not cached_image or not Path(cached_image).exists():
        retry = 3
        while retry > 0:
            try:
                resp = await async_get(url, headers)

                if resp and resp.content:
                    image = Image.open(BytesIO(resp.content)).convert('RGB')
                    image.save(file_path)
                    JsonCache.add('download_image', url, file_path)
                    return True
                else:
                    return False
            except Exception as e:
                traceback.print_exc()
                logger.error('download_image failed:', e)
                retry -= 1
                time.sleep(3)
    else:
        return cached_image

def sync_download_image(url: str, file_name: str):
    resp = requests.get(url)
    image = Image.open(BytesIO(resp.content)).convert('RGB')
    image.save(file_name)


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


def thumbnail(file_path: str, cache_dir: str, max_edge=256, min_size=64):
    path = Path(file_path)
    if not path.exists():
        return None, None
    if path.stat().st_size < min_size * 1024:
        return file_path, None

    thumb_file_path = (Path(cache_dir) / Path(file_path).stem).__str__() + '.webp'
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
    except (OSError, UnidentifiedImageError, ValueError): #PIL issues #4472 and #2445, also fixes ComfyUI issue #3416
        prev_value = ImageFile.LOAD_TRUNCATED_IMAGES
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        x = fn(arg)
    finally:
        if prev_value is not None:
            ImageFile.LOAD_TRUNCATED_IMAGES = prev_value
    return x
