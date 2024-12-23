import asyncio
import threading

import uvicorn
from data_type.init import initialize_dbs
from misc.logger import Logger
from misc.arg_parser import is_prod, host, port
from model_download_worker import ModelDownloadWorker
from prompt_worker import PromptWorker
from misc.whatsai_dirs import init_file_paths


def start_server():
    if is_prod:
        from server.server import app
        uvicorn.run(app, host=host, port=port)

    else:

        """ Warning: when you want debug prompt queue/worker, manually set reload=False, otherwise fastapi will start
            a SpawnProcess, which won't work between processes, make queue/worker no response.
        """
        uvicorn.run("server.server:app", host=host, port=port, reload=False, log_level="info")
        Logger.init_config()


def start_prompt_worker():
    loop = asyncio.new_event_loop()
    threading.Thread(target=PromptWorker.run, daemon=True, args=(loop,)).start()


def start_download_worker():
    loop = asyncio.new_event_loop()
    threading.Thread(target=ModelDownloadWorker.run, daemon=True, args=(loop,)).start()


if __name__ == '__main__':
    init_file_paths()
    initialize_dbs()

    start_prompt_worker()
    start_download_worker()

    start_server()
