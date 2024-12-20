# ref: https://gist.github.com/nkhitrov/a3e31cfcc1b19cba8e1b626276148c49, thanks.

import logging
from types import FrameType
from typing import cast

from loguru import logger as loguru_logger

from common import base_dir

log_dir = base_dir / 'log' / 'backend_manager_log'

if not log_dir.exists():
    log_dir.mkdir(parents=True)


class Logger:
    def __init__(self):
        log_path = log_dir / "whatsai_manager_log_{time:YYYY-MM-DD}.log"
        self.loguru_logger = loguru_logger
        self.loguru_logger.remove()

        self.loguru_logger.add(
            log_path,
            format='{time:YYYY-MM-DD HH:mm:ss} - '
                   "{process.name} | "
                   "{thread.name} | "
                   '{module}.{function}:{line} - {level} -{message}',
            encoding='utf-8',
            retention='7 days',
            backtrace=True,
            diagnose=True,
            enqueue=True,
            rotation="00:00"
        )

    @classmethod
    def init_config(cls):
        logging.basicConfig(handlers=[InterceptHandler()], level=0)
        LOGGER_NAMES = ("uvicorn", "uvicorn.asgi", "uvicorn.access", "fastapi", "unicorn.error")
        # change handler for default uvicorn logger
        handler = InterceptHandler()
        logging.getLogger().handlers = [handler]
        for logger_name in LOGGER_NAMES:
            logging.getLogger(logger_name).handlers = [InterceptHandler()]
            logging.getLogger(logger_name).propagate = False

        logging.root.addHandler(handler)


    def get_logger(self):
        return self.loguru_logger

class InterceptHandler(logging.Handler):

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        # Get corresponding Loguru level if it exists
        try:
            level = loguru_logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = cast(FrameType, frame.f_back)
            depth += 1
        logger = loguru_logger.bind(request_id='app')
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage(),
        )

# todo: not works properly for uvicorn, fix it.
Logger.init_config()
logger = Logger().get_logger()
