from __future__ import annotations

import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from dotenv import load_dotenv

load_dotenv()


def ensure_dir(file_path):
    """Ensure that the directory for log files exists."""
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


# Fetching environment variables for logging configuration
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

# Setup log directory and file
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
log_directory = f'../logs/{timestamp}/'
log_file = f'{log_directory}scrumbag.log'
# Ensure the log directory exists before creating file handler
ensure_dir(log_file)

# Configure logger
logger = logging.getLogger('scrumbag_logger')
logger.setLevel(
    logging.DEBUG if DEBUG else getattr(
        logging, LOG_LEVEL, logging.INFO,
    ),
)

# Create a file handler which logs messages
file_handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1)
file_handler.suffix = '%Y%m%d'
file_handler.setFormatter(
    logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    ),
)

# Add the handler to the logger
logger.addHandler(file_handler)


def log_message(level, message):
    """
    Logs a message to the configured file with the given level.
    """
    if level.lower() == 'debug':
        logger.debug(message)
    elif level.lower() == 'info':
        logger.info(message)
    elif level.lower() == 'warning':
        logger.warning(message)
    elif level.lower() == 'error':
        logger.error(message)
    elif level.lower() == 'critical':
        logger.critical(message)
    else:
        logger.info(message)


def log_debug_info(message, **kwargs):
    """
    Logs detailed debug information, including additional keyword arguments.
    """
    details = ', '.join(f'{key}={value}' for key, value in kwargs.items())
    logger.debug(f"{message} - {details}")
