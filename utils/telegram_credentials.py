from datetime import datetime
from utils.data_editor import save_data, load_data

# Function to update credentials in the JSON file
def write(user_id, user_data):
	print(f"[DBG] Writing credentials for user of: {user_id}")

	data = load_data(user_id)

	# Overwrite the 'credentials' key with the new user_data
	data["credentials"] = [user_data]

	# Save the updated data back to the JSON file
	save_data(user_id, data)

# Function to extract and format Telegram user data
def get(user):
	return {
		"username": user.username,
		"id": user.id,
		"firstName": user.first_name or "",
		"lastName": user.last_name or "",
		"isBot": user.is_bot,
		"isPremium": user.is_premium or False,
		"languageCode": user.language_code,
		"latestUpdate": datetime.now().strftime("%d/%m/%y, %H:%M:%S")
	}