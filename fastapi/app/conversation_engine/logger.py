# import logging
# import os


# log_dir = "./loggings"
# info_filename = "info.log"
# error_filename = "error.log"  # Only ERROR and CRITICAL logs go to error.log
# os.makedirs(log_dir, exist_ok=True)


# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)   


# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')


# app_log_path = os.path.join(log_dir, info_filename)
# app_handler = logging.FileHandler(app_log_path, mode='a')
# app_handler.setLevel(logging.DEBUG)
# app_handler.setFormatter(formatter)


# error_log_path = os.path.join(log_dir, "error.log")
# error_handler = logging.FileHandler(error_log_path, mode='a')
# error_handler.setLevel(logging.ERROR)
# error_handler.setFormatter(formatter)

# # Debug file handler
# debug_file_handler = logging.FileHandler('debug.log')
# debug_file_handler.setLevel(logging.DEBUG)
# debug_file_handler.setFormatter(formatter)
# logger.addHandler(debug_file_handler)

# if not logger.hasHandlers():
#     logger.addHandler(app_handler)
#     logger.addHandler(error_handler)

import logging
import os
from pathlib import Path

log_dir = Path(__file__).resolve().parents[1] / "loggings"
os.makedirs(log_dir, exist_ok=True)

class MaxLevelFilter(logging.Filter):
    """Filters (lets through) all messages with level <= max_level."""
    def __init__(self, max_level):
        super().__init__()
        self.max_level = max_level

    def filter(self, record):
        return record.levelno <= self.max_level

# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Debug handler (logs everything)
debug_handler = logging.FileHandler(os.path.join(log_dir, 'debug.log'), mode='a')
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(formatter)
logger.addHandler(debug_handler)

# Info handler (only logs INFO level)
info_handler = logging.FileHandler(os.path.join(log_dir, 'info.log'), mode='a')
info_handler.setLevel(logging.INFO)
info_handler.addFilter(MaxLevelFilter(logging.INFO))  # Logs INFO only
info_handler.setFormatter(formatter)
logger.addHandler(info_handler)

# Error handler (logs ERROR and CRITICAL)
error_handler = logging.FileHandler(os.path.join(log_dir, 'error.log'), mode='a')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)
logger.addHandler(error_handler)

# Console handler (for warnings and above)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Example usage
# logger.debug("Debug message")
# logger.info("Informational message")
# logger.warning("A warning")
# logger.error("An error occurred")
# logger.critical("Critical issue")
