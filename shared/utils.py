from __future__ import annotations

import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from dotenv import load_dotenv
# Load environment configurations if available in .env file
load_dotenv()

# Function to ensure the existence of a directory for logging
def ensure_dir(file_path):
    """
    Ensures that the directory for a given file path exists. If the directory does not exist, it is created.

    Args:
    file_path (str): The file path for which the directory is checked.
    """
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Directory created at {directory}")

# Define whether to log debug messages, influenced by the environment variable 'DEBUG'
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

# Configure the timestamp format to be used in the log file naming
timestamp = datetime.now().strftime('%Y%m%d%H')

# Set the log directory based on the current date and hour
log_directory = os.path.join('logs', timestamp)
ensure_dir(log_directory)

# Set the log file name within the log directory
log_file = os.path.join(log_directory, 'scrumbag.log')
ensure_dir(log_file)  # Ensure the log file's directory exists

# Configure the logger
logger = logging.getLogger('scrumbag_logger')
logger.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))

# Create a file handler which logs even debug messages
file_handler = TimedRotatingFileHandler(log_file, when='H', interval=1, backupCount=24)
file_handler.suffix = '%Y%m%d%H'  # Suffix for the log file name
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Add the handler to the logger
logger.addHandler(file_handler)

def log_message(level, message):
    """
    Logs a message at the specified level.

    Args:
    level (str): The log level at which to log the message ('info', 'debug', etc.).
    message (str): The message to log.
    """
    getattr(logger, level.lower(), logger.info)(message)

def log_debug_info(message, **kwargs):
    """
    Logs detailed debug information without sensitive data.

    Args:
    message (str): A descriptive message to be logged.
    **kwargs: Additional details provided as key-value pairs, filtered to ensure no sensitive information is logged.
    """
    if not DEBUG:
        return  # Skip debug logging if DEBUG is False
    filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ['client_secret', 'client_id']}
    details = ', '.join(f"{key}={value}" for key, value in filtered_kwargs.items())
    logger.debug(f"{message} - {details}")
