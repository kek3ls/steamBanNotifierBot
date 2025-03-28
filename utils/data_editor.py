import os
import json
from utils.logger import debug_print

PRIMARY_FOLDER = "userdata"

# Get the file path to the user's data
def get_user_file(userid:int):
	# debug_print('debug', f"Getting file path for {userid}")
	return f"{PRIMARY_FOLDER}/{userid}.json"

async def validate(userid:int):
	file_path = get_user_file(userid)

	# Default structure for the 'globals' section
	DEFAULT_GLOBALS = {
		"isWaitingForAccount2Add": False,
		"isWaitingForAccount2Remove": False,
		"intervalHours": 6,
		"periodicCheck": False
	}

	# Default structure for the 'trackedAccounts' section (should be a list)
	DEFAULT_TRACKED_ACCOUNTS = []

	# Default structure for the 'credentials' section (with required keys)
	DEFAULT_CREDENTIALS = {
		"username": None,
		"id": None,
		"name": {
			"name": None,
			"surname": None
		},
		"isBot": None,
		"isPremium": None,
		"languageCode": None,
		"latestUpdate": None
	}

	try:
		# Load the existing user data
		with open(file_path, "r", encoding="utf-8") as file:
			data = json.load(file)

		# Ensure 'globals' section is present and non-empty
		if not data.get("globals"):
			debug_print('warning', "'globals' is missing or empty. Overwriting with default values.")
			data["globals"] = DEFAULT_GLOBALS
		elif not all(key in data["globals"] for key in DEFAULT_GLOBALS):
			# If any key is missing from the existing "globals", we add missing keys with defaults
			for key, value in DEFAULT_GLOBALS.items():
				if key not in data["globals"]:
					data["globals"][key] = value
					debug_print('warning', f"Added missing key '{key}' to 'globals' with default value.")

		# Ensure 'trackedAccounts' section is valid (it should be a list)
		if "trackedAccounts" not in data:
			data["trackedAccounts"] = DEFAULT_TRACKED_ACCOUNTS
			debug_print('warning', "'trackedAccounts' is missing. Initializing it as an empty list.")

		# Ensure 'credentials' section contains required keys and they are set to None if missing
		if "credentials" not in data or not data["credentials"]:
			data["credentials"] = DEFAULT_CREDENTIALS
			debug_print('warning', "'credentials' is missing. Initializing it with default values.")
		else:
			# Fill missing keys in credentials with None
			for key, value in DEFAULT_CREDENTIALS.items():
				if key not in data["credentials"]:
					data["credentials"][key] = value
					debug_print('warning', f"Missing '{key}' in 'credentials'. Setting it to None.")

		await save_data(userid, data)
		return data

	except (FileNotFoundError, json.JSONDecodeError) as e:
		debug_print('error', f"Error decoding JSON data from file for {userid}: {str(e)}. Returning default data.")
		# Return default data in case of error
		return {
			"credentials": DEFAULT_CREDENTIALS,
			"trackedAccounts": DEFAULT_TRACKED_ACCOUNTS,
			"globals": DEFAULT_GLOBALS
		}

async def load_data(userid:int):
	file_path = get_user_file(userid)

	# Default structure to return if file doesn't exist or is empty
	DEFAULT_TABLE = {
		"credentials": {
			"username": None,
			"id": None,
			"name": {
				"name": None,
				"surname": None
			},
			"isBot": None,
			"isPremium": None,
			"languageCode": None,
			"latestUpdate": None
		},
		"trackedAccounts": [],
		"globals": {
			"isWaitingForAccount2Add": False,
			"isWaitingForAccount2Remove": False,
			"intervalHours": 6,
			"periodicCheck": False
		}
	}

	if not os.path.exists(PRIMARY_FOLDER):
		debug_print('info', f"Directory \"{PRIMARY_FOLDER}\" does not exist, creating it.")
		os.makedirs(PRIMARY_FOLDER)  # Ensure the directory exists

	try:
		debug_print('debug', f"Attempting to load data from: {file_path}")

		# Check if file exists and is not empty
		if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
			debug_print('warning', f"File for {userid} is empty or does not exist. Creating default data.")

			# Create the file and write the default data
			with open(file_path, "w", encoding="utf-8") as file:
				json.dump(DEFAULT_TABLE, file, indent="\t", ensure_ascii=False)

			return DEFAULT_TABLE

		with open(file_path, "r", encoding="utf-8") as file:
			data = json.load(file)

			# Call the new function to validate and fix data
			data = await validate(userid)

			debug_print('info', f"Successfully loaded and validated data for {userid}")
			return data

	except Exception as e:
		debug_print('error', f"Error decoding JSON data from file for {userid}: {str(e)}. Returning default data.")
		return DEFAULT_TABLE

# Save the user's JSON file
async def save_data(userid:int, data:dict):
	file_path = get_user_file(userid)

	try:
		debug_print('debug', f"Attempting to save data to: {file_path}")

		# Ensure the parent directory exists
		os.makedirs(os.path.dirname(file_path), exist_ok=True)

		# Write data safely
		with open(file_path, "w", encoding="utf-8") as file:
			json.dump(data, file, indent="\t", ensure_ascii=False)
			debug_print('info', f"Successfully saved data for {userid}")

	except Exception as e:
		debug_print('error', f"Error saving data for {userid}: {e}")