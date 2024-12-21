import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from common import base_dir

# Assuming base_dir is already defined somewhere in your code
log_dir = Path(base_dir) / 'log' / 'backend_manager_log'

if not log_dir.exists():
    log_dir.mkdir(parents=True)

# Define the log file path
log_path = log_dir / "whatsai_manager_log.log"

# Create a logger instance
logger = logging.getLogger("backend_manager")
logger.setLevel(logging.DEBUG)  # Set the logging level

# Create a TimedRotatingFileHandler for daily log rotation (7 days retention)
handler = TimedRotatingFileHandler(
    log_path,
    when="midnight",  # Rotate at midnight
    interval=1,  # Rotate every 1 day
    backupCount=7,  # Keep the last 7 days of logs
    encoding="utf-8"
)

# Create a log formatter
formatter = logging.Formatter(
    '%(asctime)s - %(processName)s | %(threadName)s | '
    '%(module)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s'
)

# Add the formatter to the handler
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)