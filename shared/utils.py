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

# Modify the timestamp to include only the date and hour for log rollover
timestamp = datetime.now().strftime('%Y%m%d%H')
# This sets the log directory to 'logs/YYYYMMDDHH'
log_directory = os.path.join('logs', timestamp)
ensure_dir(log_directory)

# Modify the log file name to include only the date
log_file = os.path.join(log_directory, 'scrumbag.log')
# Ensure the log directory exists
ensure_dir(log_file)

# Configure logger
logger = logging.getLogger('scrumbag_logger')
logger.setLevel(
    logging.DEBUG if DEBUG else getattr(
        logging, LOG_LEVEL, logging.INFO,
    ),
)

# Create a file handler which logs messages
# Set 'when' to 'H' for hourly rollover and 'midnight' for daily rollover
file_handler = TimedRotatingFileHandler(
    log_file, when='H', interval=1, backupCount=24,
)  # Keep last 24 hours of logs
file_handler.suffix = '%Y%m%d%H'  # Suffix for the log file name
file_handler.setFormatter(
    logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    ),
)

# Add the handler to the logger
logger.addHandler(file_handler)


def log_message(level, message):
    """Logs a message with the given level."""
    # Note that for debug level, we might avoid logging it in production
    getattr(logger, level.lower(), logger.info)(message)


def log_debug_info(message, **kwargs):
    """Logs debug information without sensitive details."""
    if not DEBUG:
        # In production, you might want to skip debug messages entirely
        return
    # Filter out any sensitive data from kwargs before logging
    filtered_kwargs = {
        k: v for k, v in kwargs.items() if k not in [
            'client_secret', 'client_id',
        ]
    }
    details = ', '.join(
        f'{key}={value}' for key, value in filtered_kwargs.items()
    )
    logger.debug(f"{message} - {details}")
