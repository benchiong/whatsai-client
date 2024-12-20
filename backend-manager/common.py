import platform
from pathlib import Path

is_win = is_macos = is_linux = False
system_info = platform.system().lower()
if system_info == 'darwin':
    is_macos = True
elif system_info == 'linux':
    is_linux = True
elif system_info == 'windows':
    is_win = True
else:
    print("Unknown system")

dir_name = 'whatsai'
if is_win:
    base_dir = Path("D:/") / dir_name
else:
    base_dir = Path.home() / dir_name

tmp_dir = base_dir / 'tmp'
backend_local_path = base_dir / 'backend'
venv_path = base_dir / 'venv'

base_dir.mkdir(exist_ok=True)
tmp_dir.mkdir(exist_ok=True)

backend_install_progress_info = {}

def get_backend_install_progress_info():
    return backend_install_progress_info

def update_backend_install_progress_info(stage, info, progress=None):
    global backend_install_progress_info
    backend_install_progress_info = {
        'stage': stage,
        'info': info,
        'progress': progress
    }

