import os
import sys
import inspect
import logging
import traceback
from datetime import datetime

# Ensure the logs directory exists
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Get the current date for the log file name
log_file_name = datetime.now().strftime('%d-%B-%y')
log_file = os.path.join(log_dir, f"{log_file_name}.log")

# Set up the logger
logger = logging.getLogger("debug_logger")
logger.setLevel(logging.DEBUG)

# Create a file handler for logging
file_handler = logging.FileHandler(log_file, encoding="utf-8")  # Ensure UTF-8 encoding
file_handler.setLevel(logging.DEBUG)

# Define log format
formatter = logging.Formatter(
	'%(asctime)s - %(caller)s - [%(levelname)s] - %(message)s',
	datefmt='%H:%M:%S'
)
file_handler.setFormatter(formatter)

# Add handler to the logger
logger.addHandler(file_handler)

# Function to extract caller details
def get_caller_info():
	frame = inspect.stack()[2]  # Get the caller frame
	filename = frame.filename.replace("\\", "/")  # Normalize path for consistency
	line_number = frame.lineno

	# Find the position of "@steamBanNotifierBot" in the path
	MARKER = "@steamBanNotifierBot"
	if MARKER in filename:
		filename = filename.split(MARKER, 1)[-1]  # Keep everything after the marker
		if filename.startswith("/"):
			filename = filename[1:]  # Remove leading slash if present

	return f"{filename}:{line_number}"

# Secure and formatted logging function
def debug_print(level: str, message: str, caller: str = None):
	"""Secure logging function that includes caller details"""

	# If caller is None, get it from the stack (except when logging an unhandled exception)
	if caller is None:
		caller = get_caller_info()  # Get caller file and line number

	# Log data dictionary
	log_data = {"caller": caller}

	if level == 'debug':
		logger.debug(message, extra=log_data)
		print(f"{datetime.now().strftime('%H:%M:%S')} - {caller} - [DBG] - {message}")
	elif level == 'info':
		logger.info(message, extra=log_data)
		print(f"{datetime.now().strftime('%H:%M:%S')} - {caller} - [INF] - {message}")
	elif level == 'warning':
		logger.warning(message, extra=log_data)
		print(f"{datetime.now().strftime('%H:%M:%S')} - {caller} - [WRN] - {message}")
	elif level == 'error':
		logger.error(message, extra=log_data)
		print(f"{datetime.now().strftime('%H:%M:%S')} - {caller} - [ERR] - {message}")
	elif level in ['critical', 'fatal']:
		logger.critical(message, extra=log_data)
		print(f"{datetime.now().strftime('%H:%M:%S')} - {caller} - [FATAL] - {message}")
	else:
		logger.info(f"[UNKNOWN] {message}", extra=log_data)
		print(f"{datetime.now().strftime('%H:%M:%S')} - {caller} - [UNK] - {message}")

def exception_handler(exc_type, exc_value, exc_traceback):
    """Logs uncaught exceptions"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return  # Allow Ctrl+C to terminate the script normally

    error_message = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
	
    # Also call debug_print to ensure it works
    debug_print("critical", f"Unhandled Exception:\n{error_message}", caller="sys.excepthook")

# Override default exception hook
sys.excepthook = exception_handler