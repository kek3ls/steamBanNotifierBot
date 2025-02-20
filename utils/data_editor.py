import os
import json

# Get the file path for a specific user's data
def get_user_file(user_id):
	return f"user_data/{user_id}.json"

# Load data from a user-specific JSON file
def load_data(user_id):
	file_path = get_user_file(user_id)
	
	if not os.path.exists("user_data"):
		os.makedirs("user_data")  # Ensure the directory exists

	try:
		with open(file_path, "r") as file:
			return json.load(file)
	except (FileNotFoundError, json.JSONDecodeError):
		return {"tracked_accounts": []}  # Default empty list for new users

# Save data to a user-specific JSON file
def save_data(user_id, data):
	file_path = get_user_file(user_id)
	with open(file_path, "w") as file:
		json.dump(data, file, indent=4)