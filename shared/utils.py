from __future__ import annotations

import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from dotenv import load_dotenv

load_dotenv()


def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
log_directory = f'../logs/{timestamp}/'
log_file = f'{log_directory}scrumbag.log'
ensure_dir(log_file)

logger = logging.getLogger('scrumbag_logger')
logger.setLevel(
    logging.DEBUG if DEBUG else getattr(
        logging, LOG_LEVEL, logging.INFO,
    ),
)

file_handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1)
file_handler.suffix = '%Y%m%d'
file_handler.setFormatter(
    logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    ),
)

logger.addHandler(file_handler)


def log_message(level, message):
    """Logs a message with the given level."""
    getattr(logger, level.lower(), logger.info)(message)


def log_debug_info(message, **kwargs):
    """Logs debug information without sensitive details."""
    details = ', '.join(
        f'{key}={value}' for key,
        value in kwargs.items() if key != 'client_secret'
    )
    logger.debug(f"{message} - {details}")
