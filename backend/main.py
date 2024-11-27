import asyncio
import threading

import uvicorn
from misc.argparser import args
from misc.logger import logger, Logger
from misc.prompt_worker import PromptWorker
from misc.whatsai_dirs import init_file_paths


def start_server():
    is_dev = True if args.env == 'dev' else False

    if is_dev:

        """ Warning: when you want debug prompt queue/worker, manually set reload=False, otherwise fastapi will start
            a SpawnProcess, which won't work between processes, make queue/worker no response.
        """
        uvicorn.run("server.server:app", host=args.host, port=args.port, reload=False, log_level="info")
        Logger.init_config()

    else:
        from server.server import app
        uvicorn.run(app, host=args.host, port=args.port)

def start_worker():
    loop = asyncio.new_event_loop()
    threading.Thread(target=PromptWorker.run, daemon=True, args=(loop,)).start()
    logger.debug("worker started.")

if __name__ == '__main__':
    init_file_paths()
    start_worker()
    start_server()






