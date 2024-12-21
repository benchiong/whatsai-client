import asyncio
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware

from logger import logger
from common import backend_local_path, update_backend_install_progress_info, \
    get_backend_install_progress_info, is_macos, is_win
from router_process import router as process_router
import backend_manager
from router_python import router as python_router, is_python_ready, find_python_venv_executable_path, install_python
from router_github import router as github_router, is_backend_codes_ready, \
    download_backend_codes_and_install_dependencies
from router_gpu import router as gpu_router
from utils import find_available_port, async_get

router = APIRouter()

@router.get('/')
async def index():
    return 'ok'

@router.get('/run_backend')
async def start_to_run_backend():
    await run_backend()

@router.get('/stop_backend')
async def _stop_backend():
    await stop_backend()


_backend_port = 8172
@router.get("/backend_port")
async def backend_port():
    global _backend_port
    return _backend_port

@router.get("/is_backend_ready")
async def is_backend_ready():
    global _backend_port

    python_ok = is_python_ready()
    repo_ok = is_backend_codes_ready()
    ready = python_ok and repo_ok

    if not ready:
        return {
            'backend_running': False,
            'ready': False,
            'port': None
        }

    backend_url = f'http://127.0.0.1:{_backend_port}/docs#/'
    try:
        response = await async_get(backend_url, retry=1)
        if response and response.status_code == 200:
            return {
                'backend_running': True,
                'ready': ready,
                'port': _backend_port
            }
        else:
            return {
                'backend_running': False,
                'ready': ready,
                'port': None
            }
    except Exception as e:
        return {
            'backend_running': False,
            'ready': ready,
            'port': None
        }

installing = False
@router.get("/install_everything")
async def install_everything():
    global installing
    if installing:
        return
    installing = True
    update_backend_install_progress_info(stage='Installing python...',
                                         info='Start to install python/venv/pytorch, may take some time',
                                         )
    python_success = await install_python()
    if not python_success:
        return False
    success = await download_backend_codes_and_install_dependencies()
    if success:
        all_success = await run_backend()
        if all_success:
            update_backend_install_progress_info(stage='ready',
                                                 info='Env are prepared, try to start backend.',
                                                 )
    else:
        update_backend_install_progress_info(stage='failed',
                                             info='failed to install, retry may help.',
                                             )

@router.get("/install_progress_info")
async def install_progress_info():
    return get_backend_install_progress_info()


@asynccontextmanager
async def lifespan(app: FastAPI):
    add_possible_python_paths()
    await run_backend()

    yield

    if backend_manager.manager:
        await backend_manager.manager.stop_process()

app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.include_router(process_router, prefix='/process')
app.include_router(python_router, prefix='/python')
app.include_router(github_router, prefix='/github')
app.include_router(gpu_router, prefix='/gpu')


def add_possible_python_paths():
    python_executable = sys.executable
    python_dir = os.path.dirname(python_executable)

    logger.info(f"Current Python executable: {python_executable}")
    logger.info(f"Current Python directory: {python_dir}")

    current_path = os.environ.get('PATH', '')

    logger.debug(f"is_macos: {is_macos}")
    if is_macos:
        homebrew_path = "/opt/homebrew/bin"
        macos_system_python = "/usr/local/bin"
        python_312_path = "/Library/Frameworks/Python.framework/Versions/3.12/bin"

        for path in [homebrew_path, macos_system_python, python_312_path]:
            if os.path.exists(path) and path not in current_path:
                os.environ['PATH'] = f"{path}{os.pathsep}{os.environ['PATH']}"
                logger.info(f"Added {path} to PATH")
            else:
                logger.info(f"{path} not exists.")

    if is_win:
        windows_paths = [
            "C:\\Python312",
            "C:\\Program Files\\Python312",
            "C:\\Program Files (x86)\\Python312",
        ]
        for path in windows_paths:
            if os.path.exists(path) and path not in current_path:
                os.environ['PATH'] = f"{path}{os.pathsep}{os.environ['PATH']}"
                print(f"Added {path} to PATH")

async def run_backend():
    global _backend_port
    logger.info(f"is_python_ready: {is_python_ready()} is_backend_codes_ready: {is_backend_codes_ready()}")
    if is_python_ready() and is_backend_codes_ready():
        python_executable = find_python_venv_executable_path()
        backend_main = backend_local_path / 'main.py'
        command = [str(python_executable), str(backend_main)]
        available_port = find_available_port(_backend_port)
        _backend_port = available_port
        port_arg = [f"--port={available_port}"]
        prod_arg = ['--prod']
        command = command + port_arg + prod_arg
        logger.info(command)
        backend_manager.manager = backend_manager.AsyncProcessManager(command)
        await backend_manager.manager.start_process()
        _ = asyncio.create_task(backend_manager.manager.monitor_process())
        return True
    return False


async def stop_backend():
    backend_manager.manager.monitor = False
    await backend_manager.manager.stop_process()

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )
