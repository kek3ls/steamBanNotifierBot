# credentials_manager.py
import json
import os

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
        return {"tracked_accounts": [], "credentials": [], "interval_hours": 6}

# Save data to a user-specific JSON file
def save_data(user_id, data):
    file_path = get_user_file(user_id)
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

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