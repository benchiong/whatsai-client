import subprocess

from common import is_win, is_linux, is_macos
from logger import logger

from fastapi import APIRouter

router = APIRouter()

# todo: fully test
def macos_gpu():
    try:
        output = subprocess.check_output(["system_profiler", "SPDisplaysDataType"], text=True)
        if "AMD" in output:
            return "AMD"
        elif "NVIDIA" in output:
            return "NVIDIA"
        elif "Intel" in output:
            return "Intel"
        elif "Apple" in output:
            return "Apple"
        else:
            return "Unknown"
    except Exception as e:
        return "Unknown"

def is_apple_m_series_chip():
    if not is_macos:
        return False
    try:
        output = subprocess.check_output(["system_profiler", "SPHardwareDataType"], text=True)
        for line in output.splitlines():
            if "Chip:" in line:
                chip_info = line.split(":", 1)[1].strip()
                return "M" in chip_info
        return False
    except Exception as e:
        logger.info("is_apple_m_series_chip error:", e)
        return False

def win_gpu():
    try:
        output = subprocess.check_output(
            ["wmic", "path", "win32_VideoController", "get", "name"], text=True
        )
        output = output.strip().lower()
        if "amd" in output:
            return "AMD"
        elif "nvidia" in output:
            return "NVIDIA"
        elif "intel" in output:
            return "Intel"
        else:
            return "Unknown"
    except Exception as e:
        return "Unknown"

def linux_gpu():
    try:
        output = subprocess.check_output(["lspci"], text=True)
        if "AMD" in output or "Radeon" in output:
            return "AMD"
        elif "NVIDIA" in output:
            return "NVIDIA"
        elif "Intel" in output:
            return "Intel"
        else:
            return "Unknown"
    except Exception as e:
        return "Unknown"

def gpu_info():
    if is_macos:
        return macos_gpu()
    if is_linux:
        return linux_gpu()
    if is_win:
        return win_gpu()
    return 'Unknown'

@router.get('/gpu_info')
def get_gpu_info():
    return gpu_info()

@router.get('/is_apple_m_series_chip')
def apple_m_series_chip():
    return is_apple_m_series_chip()

