# utils/logger.py

import logging
import os
import sys
from datetime import datetime
from utils.settings import BASE_DIR, LOG_SETTINGS, LANGCHAIN_DEBUG, ENABLE_CONSOLE_OUTPUT

# Using LANGCHAIN_DEBUG from settings to control the debug mode
DEBUG_MODE = LANGCHAIN_DEBUG  # If you need to output details including traceback，change it to True

# Make log_level(string) from LOG_SETTINGS trans to levels of logging
log_level = getattr(logging, LOG_SETTINGS.get('log_level', 'INFO').upper(), logging.INFO)

# Create dict by settings
LOG_DIR_ABS = os.path.join(BASE_DIR, LOG_SETTINGS.get('log_dir', 'logs'))
os.makedirs(LOG_DIR_ABS, exist_ok=True)

# Get the name of the main script
main_script = os.path.basename(sys.argv[0])
main_script_name = os.path.splitext(main_script)[0]
LOG_FILE = os.path.join(LOG_DIR_ABS, f"{main_script_name}_{datetime.now().strftime('%Y%m%d')}.log")


# Console filter：only allow attribute of True in 'print_console' to be output
class ConsoleFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return getattr(record, 'print_console', False)


# Custom console formatter：Detailed exception information is not output in non-debug mode（traceback）
class MinimalConsoleFormatter(logging.Formatter):
    def format(self, record):
        if not DEBUG_MODE and record.exc_info:
            record.exc_info = None
            record.exc_text = None
        return super().format(record)


# Config root logger（only initial once）
if not logging.getLogger().hasHandlers():
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # file processor：Output all logs to log file（include all traceback）
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(LOG_SETTINGS.get('log_format')))
    root_logger.addHandler(file_handler)

    # Console processor：Output only when ENABLE_CONSOLE_OUTPUT is True, and use MinimalConsoleFormatter
    if ENABLE_CONSOLE_OUTPUT:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(MinimalConsoleFormatter(LOG_SETTINGS.get('log_format')))
        console_handler.addFilter(ConsoleFilter())
        root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Obtain the logger object with the specified name。
    """
    return logging.getLogger(name)