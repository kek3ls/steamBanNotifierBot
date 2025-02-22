import logging
from datetime import datetime

# Set up custom logger
logger = logging.getLogger("debug_logger")
logger.setLevel(logging.DEBUG)

# Create a file handler to store logs in a file
file_handler = logging.FileHandler("debug_logs.txt")
file_handler.setLevel(logging.DEBUG)

# Create a formatter and attach it to the handler
formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

# Add handler to the logger
logger.addHandler(file_handler)

# Function to print and log messages
def debug_print(level: str, message: str):
	"""
	Custom print function that logs messages with a specified level.
	Levels: 'DBG', 'INF', 'WRN', 'ERR'
	"""
	timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	# Choose the correct logging method based on the level
	if level == 'DBG':
		logger.debug(f"{timestamp} - [DBG] - {message}")
	elif level == 'INF':
		logger.info(f"{timestamp} - [INF] - {message}")
	elif level == 'WRN':
		logger.warning(f"{timestamp} - [WRN] - {message}")
	elif level == 'ERR':
		logger.error(f"{timestamp} - [ERR] - {message}")
	else:
		logger.info(f"{timestamp} - [INFO] - {message}")  # Default to info if level is unknown

	# Also print to console (for real-time feedback)
	print(f"{timestamp} - [{level}] - {message}")