import subprocess
import zipfile
from pathlib import Path
from logger import logger

from fastapi import APIRouter

from common import base_dir, tmp_dir, backend_local_path, backend_install_progress_info, \
    update_backend_install_progress_info
from router_python import find_python_venv_executable_path
from utils import async_get, read_from_file, write_to_file, clear_tmp, download_file, copy_folder, \
    is_folder_exists_and_not_empty

router = APIRouter()

github_repo_latest_version_url = 'https://github.com/benchiong/whatsai-client/releases/latest'
github_repo_download_url = 'https://codeload.github.com/benchiong/whatsai-client/zip/refs/heads/main'
version_local_file = base_dir / 'current_version'
tmp_backend_file = (tmp_dir / 'main.zip').__str__()
tmp_backend_dir = tmp_dir / 'whatsai-client-main' / 'backend'

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
        logger.info('Backend dir exits')
        return True

    def _callback(percent, downloaded_size, total_size):
        update_backend_install_progress_info(stage='Downloading backend files...',
                                             info=f'',
                                             progress={
                                                 'percent': percent,
                                                 'downloaded_size': downloaded_size,
                                                 'total_size': total_size
                                             })
    download_success = await download_file(github_repo_download_url, tmp_backend_file, callback=_callback)
    if not download_success:
        return False

    with zipfile.ZipFile(tmp_backend_file, 'r') as zip_ref:
        zip_ref.extractall(tmp_dir.__str__())
    if tmp_backend_dir.exists():
        copy_folder(tmp_backend_dir.__str__(), backend_local_path.__str__())
    if is_folder_exists_and_not_empty(backend_local_path.__str__()):
        version = await get_latest_release_version()
        set_current_release_version(version)
        clear_tmp()
        logger.info(f"Backend files are ready, path: {backend_local_path.__str__()}")
        update_backend_install_progress_info(stage='Backend files downloaded.',
                                             info='',
                                             )
        return True
    return False

def install_dependencies_in_venv():
    update_backend_install_progress_info(stage='Installing dependencies... ',
                                         info='',
                                         )
    requirements_file = backend_local_path / 'requirements.txt'
    if not requirements_file.exists():
        logger.info("requirements.txt not exits")
        return False
    python_venv_executable = find_python_venv_executable_path()
    install_command = [str(python_venv_executable), "-m", "pip", "install", "-r", str(requirements_file)]
    try:
        update_backend_install_progress_info(stage='Installing dependencies...',
                                             info=f'',
                                             )
        subprocess.run(install_command, check=True)
        logger.info("Dependencies installed successfully from requirements.txt.")
        update_backend_install_progress_info(stage='Install dependencies done,',
                                             info=f'',
                                             )
        return True
    except subprocess.CalledProcessError as e:
        logger.info(f"Failed to install dependencies: {e}")
        update_backend_install_progress_info(stage='failed',
                                             info='failed to install dependencies,retry may help.',
                                             )
        return False


async def download_backend_codes_and_install_dependencies(update=False):
    update_backend_install_progress_info(stage='start to download backend codes',
                                         info='it will take some time.',
                                         )
    file_download_success = await download_folder(update)
    if not file_download_success:
        return False
    return install_dependencies_in_venv()


def is_backend_codes_ready():
    return is_folder_exists_and_not_empty(backend_local_path)

@router.get('/get_latest_release_version')
async def latest_release_version():
    return await get_latest_release_version()
@router.get('/get_local_current_version')
async def get_local_current_version():
    return get_current_release_version()

@router.get('/is_backend_repo_ready')
async def is_backend_repo_ready():
    return is_backend_codes_ready()

@router.get('/download_backend_codes_and_install_dependencies')
async def _download_backend_codes_and_install_dependencies():
    return await download_backend_codes_and_install_dependencies()

