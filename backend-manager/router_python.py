import os
import subprocess
from pathlib import Path

from logger import logger
from fastapi import APIRouter

from common import is_win, is_linux, is_macos, tmp_dir, venv_path, update_backend_install_progress_info
from router_gpu import is_apple_m_series_chip, gpu_info
from utils import download_file, is_folder_exists_and_not_empty

router = APIRouter()

python_version = '3.12.7'
def python_installed():
    try:
        python_cmd = find_system_python_executable()
        if not python_cmd:
            return False
        result = subprocess.check_output([python_cmd, "--version"])
        installed_version = result.decode().strip().split()[-1]
        major, minor, _ = installed_version.split(".")
        return str(major) == "3" and str(minor) == "12"
    except FileNotFoundError:
        return False

async def download_and_install_python():
    update_backend_install_progress_info(stage='Try to download python,', info='preparing...')
    if is_macos:
        await download_and_install_python_on_macos()
    elif is_linux:
        await download_and_install_python_on_linux()
    elif is_win:
        await download_and_install_python_on_windows()
    else:
        logger.info("Unsupported system.")

def install_pkg_with_popup(installer_path):
    if not os.path.exists(installer_path):
        raise FileNotFoundError(f"Installer not found at {installer_path}")

    update_backend_install_progress_info(stage='Install python,',
                                         info=f'please agree to install.')
    message = (
        "This process will install Python 3.12.7 on your system.\n\n"
        "It is required for running the application. "
        "Please confirm to proceed with the installation."
    )

    script = f"""
        tell application "System Events"
            set response to display dialog "{message}" buttons {{"Cancel", "Proceed"}} default button "Proceed"
        end tell
        return button returned of result
        """

    # Use osascript to trigger the GUI installer
    try:
        result = subprocess.check_output(["osascript", "-e", script]).decode().strip()
        if result == "Proceed":
            subprocess.check_call([
                "osascript",
                "-e",
                f'do shell script "sudo installer -pkg \\"{installer_path}\\" -target /" with administrator privileges'
            ])
            logger.info("Python installation completed successfully.")
            update_backend_install_progress_info(stage='Install python,',
                                                 info=f'python installed.')
        else:
            update_backend_install_progress_info(stage='Install python,',
                                                 info=f'You canceled install, please quit and restart.')
            logger.info("Installation canceled by user.")
    except subprocess.CalledProcessError as e:
        logger.info(f"Installation failed: {e}")

async def download_and_install_python_on_macos():
    python_installer_url = f"https://www.python.org/ftp/python/{python_version}/python-{python_version}-macos11.pkg"
    installer_path = (tmp_dir / f'python-{python_version}-macos11.pkg').__str__()
    logger.info(python_installer_url, installer_path)
    update_backend_install_progress_info(stage='Install python,', info=f'checking download url: {python_installer_url}')

    def _callback(percent, downloaded_size, total_size):
        if percent and downloaded_size and total_size:
            update_backend_install_progress_info(stage='Downloading python installation file,',
                                                 info=f'',
                                                 progress={
                                                     'percent': percent,
                                                     'downloaded_size': downloaded_size,
                                                     'total_size': total_size
                                                 })
    success = await download_file(python_installer_url, installer_path, callback=_callback)

    if success:
        update_backend_install_progress_info(stage='Install python,',
                                             info=f'python downloading done.')
        install_pkg_with_popup(installer_path)

async def download_and_install_python_on_linux():
    # todo, full version of install method ubuntu/debian/redhat...
    subprocess.check_call(["sudo", "apt", "install", "python3.12", "python3.12-venv", "python3.12-dev"])

async def download_and_install_python_on_windows():
    python_installer_url = f"https://www.python.org/ftp/python/{python_version}/python-{python_version}.exe"
    installer_path = (tmp_dir / f'python-{python_version}.exe').__str__()
    logger.info(python_installer_url, installer_path)
    update_backend_install_progress_info(stage='Install python,', info=f'downloading python file: {python_installer_url}')
    success = await download_file(python_installer_url, installer_path)
    if success:
        subprocess.check_call([installer_path, "/quiet", "InstallAllUsers=1", "PrependPath=1"])

def find_system_python_executable():
    python_versions = ["python3", "python"]
    for python_version in python_versions:
        try:
            result = subprocess.run(
                [python_version, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if "3.12" in result.stdout or "3.12" in result.stderr:
                return python_version
        except FileNotFoundError:
            continue
    return None
def create_venv(python_executable, venv_path):
    logger.info(f"Creating virtual environment at {venv_path}...")
    update_backend_install_progress_info(stage='Creating venv,', info=f'creating...')

    if Path(venv_path).exists():
        logger.info(f"Venv: {venv_path.__str__()} already exits.")
        return True
    try:
        subprocess.check_call([python_executable, "-m", "venv", venv_path])
        logger.info(f"Virtual environment created at {venv_path}.")
        update_backend_install_progress_info(stage='Venv created,', info=f'path: {str(venv_path)}')

        return True
    except subprocess.CalledProcessError as e:
        logger.info(f"Failed to create virtual environment: {e}")
        update_backend_install_progress_info(stage='failed', info=f'venv creating failed, retry may help')
        return False

def find_python_venv_executable_path():
    if is_win:
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / 'python'


# https://github.com/comfyanonymous/ComfyUI?tab=readme-ov-file#installing
def install_pytorch():
    venv_python_executable = find_python_venv_executable_path()
    if not venv_python_executable.exists():
        logger.info(f"Python executable not found in venv: {venv_python_executable}")
        return False
    gpu = gpu_info()
    if gpu == 'NVIDIA':
        install_command = [
            str(venv_python_executable), "-m", "pip", "install",
            "torch", "torchvision", "torchaudio",
            "--extra-index-url", "https://download.pytorch.org/whl/cu124"
        ]
    elif gpu == 'AMD':
        if is_linux:
            install_command = [
                str(venv_python_executable), "-m", "pip", "install",
                "torch", "torchvision", "torchaudio",
                "--index-url", "https://download.pytorch.org/whl/rocm6.2"
            ]
        else:
            # todo:
            install_command = None
    elif gpu == 'Intel':
        install_command = None
    elif gpu == 'Apple':
        if is_apple_m_series_chip():
            install_command = [
                str(venv_python_executable), "-m", "pip", "install",
                "--pre", "torch", "torchvision", "torchaudio",
                "--extra-index-url", "https://download.pytorch.org/whl/nightly/cpu"
            ]
        else:
            # todo:
            install_command = None
    else:
        install_command = None

    if not install_command:
        logger.info(f"Unsupported gpu: {gpu}")
        return

    try:
        subprocess.run(install_command, check=True)
        logger.info("PyTorch installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.info(f"Failed to install PyTorch: {e}")
        return False

def venv_ready():
    return is_folder_exists_and_not_empty(venv_path)

def check_torch_installed():
    venv_python_executable = find_python_venv_executable_path()

    try:
        result = subprocess.run(
            [venv_python_executable, "-c", "import torch; print(torch.__version__)"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"torch version: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        logger.info(f"Error: {e}")
        return False

def is_python_ready():
    is_python_installed = python_installed()
    logger.info(f"is_python_installed: {is_python_installed}")
    if not is_python_installed:
        return False
    is_venv_ready = venv_ready()
    logger.info(f"is_venv_ready: {is_venv_ready}")
    if not is_venv_ready:
        return False
    is_torch_installed = check_torch_installed()
    logger.info(f'is_torch_installed: {is_torch_installed}')
    return is_torch_installed

async def install_python():
    update_backend_install_progress_info(stage='Checking python version', info='checking...')
    is_python_installed = python_installed()
    if not is_python_installed:
        await download_and_install_python()
    is_python_installed = python_installed()
    if not is_python_installed:
        update_backend_install_progress_info(stage='failed', info='Python install failed, retry may help.')
        return False

    logger.info(f"is python: {python_version} installed: {is_python_installed}")
    update_backend_install_progress_info(stage='Python installed, start to install venv', info=f'python version: {python_version}')
    python_executable = find_system_python_executable()
    venv_success = create_venv(python_executable, venv_path.__str__())
    if not venv_success:
        update_backend_install_progress_info(stage='failed', info='Venv installed failed, retry may help.')
        return False
    update_backend_install_progress_info(stage='Installing pytorch,', info=f'')
    pytorch_success = install_pytorch()
    if pytorch_success:
        update_backend_install_progress_info(stage='Pytorch installed,', info=f'')
    else:
        update_backend_install_progress_info(stage='failed', info=f'Failed to install pytorch,retry may help.')
    return pytorch_success

@router.get('/install_python')
async def _install_python():
    return await install_python()
@router.get('/is_python_ready')
def _is_python_ready():
    return is_python_ready()

