import os
import json

# Get the file path for a specific user's data
def get_user_file(user_id):
	print(f"[DBG] Getting file path for user_id: {user_id}")
	return f"user_data/{user_id}.json"

# Load data from a user-specific JSON file
def load_data(user_id):
	file_path = get_user_file(user_id)

	if not os.path.exists("user_data"):
		print("[INF] Directory 'user_data' does not exist, creating it.")
		os.makedirs("user_data")  # Ensure the directory exists

	try:
		print(f"[DBG] Attempting to load data from: {file_path}")
		with open(file_path, "r", encoding="utf-8") as file:
			data = json.load(file)
			print(f"[INF] Successfully loaded data for user_id: {user_id}")
			return data
	except FileNotFoundError:
		print(f"[WRN] File for user_id {user_id} not found. Returning default data.")
		return {"trackedAccounts": []}  # Default empty list for new users
	except json.JSONDecodeError:
		print(f"[ERR] Error decoding JSON data from file for user_id {user_id}. Returning default data.")
		return {"trackedAccounts": []}

def save_data(user_id, data):
	file_path = get_user_file(user_id)

	try:
		# Check if the file exists and if so, compare the data
		if os.path.exists(file_path):
			with open(file_path, "r", encoding="utf-8") as file:
				existing_data = json.load(file)

			# If the data is the same, do not save to avoid excessive disk usage
			if existing_data == data:
				print(f"[INF] Data for user_id {user_id} is the same. No need to save.")
				return

		# If data is different, save it
		print(f"[DBG] Attempting to save data to: {file_path}")
		with open(file_path, "w", encoding="utf-8") as file:
			json.dump(data, file, indent="\t", ensure_ascii=False)
			print(f"[INF] Successfully saved data for user_id: {user_id}")

	except Exception as e:
		print(f"[ERR] Error saving data for user_id {user_id}: {e}")