import asyncio
import sys
import threading

import uvicorn

from misc.logger import logger, Logger
from misc.options import env, host, port
from misc.prompt_worker import PromptWorker
from misc.whatsai_dirs import init_file_paths
from misc.whatsai_dirs import base_dir

comfy_outer_path = base_dir
sys.path.append(comfy_outer_path.__str__())


def start_server():
    is_dev = True if env == 'dev' else False

    if is_dev:

        """ Warning: when you want debug prompt queue/worker, manually set reload=False, otherwise fastapi will start
            a SpawnProcess, which won't work between processes, make queue/worker no response.
        """
        uvicorn.run("server.server:app", host=host, port=port, reload=False, log_level="info")
        Logger.init_config()

    else:
        from server.server import app
        uvicorn.run(app, host=host, port=port)


def start_worker():
    loop = asyncio.new_event_loop()
    threading.Thread(target=PromptWorker.run, daemon=True, args=(loop,)).start()
    logger.debug("worker started.")


if __name__ == '__main__':
    init_file_paths()
    start_worker()
    start_server()
