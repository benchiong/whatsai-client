from pathlib import Path

from fastapi import APIRouter

from common import base_dir, tmp_dir
from utils import async_get, read_from_file, write_to_file, clear_tmp, download_file

router = APIRouter()

github_repo_latest_version_url = 'https://github.com/benchiong/whatsai-client/releases/latest'
github_repo_download_url = 'https://codeload.github.com/benchiong/whatsai-client/zip/refs/heads/main'
version_local_file = base_dir / 'current_version'
backend_local_path = base_dir / 'backend'
tmp_backend_file = (tmp_dir / 'main.zip').__str__()

async def get_latest_release_version():
    response = await async_get(github_repo_latest_version_url)
    if response.status_code == 302:
        redirect_url = response.headers.get('Location')
        if redirect_url:
            tag_name = Path(redirect_url).name
            return tag_name
    return None

def get_current_release_version():
    return read_from_file(version_local_file.__str__())

def set_current_release_version(version):
    return write_to_file(version_local_file.__str__(), version)
async def download_folder(update=False, callback=None):
    if backend_local_path.exists() and not update:
        print('Backend dir exits')
        return
    success = await download_file(github_repo_download_url, tmp_backend_file, callback=callback)
    return success

@router.get('/get_latest_release_version')
async def latest_release_version():
    return await get_latest_release_version()
@router.get('/get_local_current_version')
async def get_local_current_version():
    return get_current_release_version()

@router.get('/download_backend_codes')
async def download_backend_codes():
    success = await download_folder()
    print(success)
