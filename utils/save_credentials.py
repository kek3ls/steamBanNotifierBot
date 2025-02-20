from utils.data_editor import save_data, load_data

# Function to update credentials in the JSON file
def update_user_credentials(user_id, user_data):
	data = load_data(user_id)

	# Ensure the 'credentials' key exists
	if 'credentials' not in data:
		data['credentials'] = []

	# Check if the user credentials already exist in the data
	if not any(cred['username'] == user_data['username'] for cred in data['credentials']):
		data["credentials"].append(user_data)

	# Save the updated data back to the JSON file
	save_data(user_id, data)

# Function to extract and format Telegram user data
def extract_telegram_user_data(user):
	return {
		"username": user.username,
		"id": user.id,
		"firstName": user.first_name,
		"lastName": user.last_name,
		"isBot": user.is_bot,
		"isPremium": user.is_premium,
		"languageCode": user.language_code,
	}