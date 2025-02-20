import json
import os
from telegram import Update
from telegram.ext import CallbackContext
from utils.steamid_conversion import convert_to_steamid64
from utils.save_credentials import update_user_credentials, extract_telegram_user_data

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
        return {"tracked_accounts": [], "interval_hours": 6}

# Save data to a user-specific JSON file
def save_data(user_id, data):
    file_path = get_user_file(user_id)
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

# Function to handle the "/add" command (adding new accounts)
async def add_account(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id  # Get the user's Telegram ID

    # Extract the user's credentials from the Telegram update
    telegram_user_data = extract_telegram_user_data(update.message.from_user)

    # Update the user's credentials in the JSON file
    update_user_credentials(user_id, telegram_user_data)

    if len(context.args) == 0:
        await update.message.reply_text(
            "❌ Please provide a valid Steam account input.\n\n"
            "I accept these types:\nSteamID64 (12345678901234567)\n"
            "Steam profile url (https://steamcommunity.com/profiles/12345678901234567)\n"
            "Steam custom profile url (https://steamcommunity.com/id/xxx)\n"
            "SteamID3 ([U:1:12345678])\n"
            "Steam shortened url (https://s.team/p/abcd-dcba)"
        )
        return

    input_str = context.args[0]
    steamid64 = await convert_to_steamid64(input_str)

    if not steamid64:
        await update.message.reply_text(
            "❌ Please provide a valid Steam account input.\n\n"
            "I accept these types:\nSteamID64 (12345678901234567)\n"
            "Steam profile url (https://steamcommunity.com/profiles/12345678901234567)\n"
            "Steam custom profile url (https://steamcommunity.com/id/xxx)\n"
            "SteamID3 ([U:1:12345678])\n"
            "Steam shortened url (https://s.team/p/abcd-dcba)"
        )
        return

    data = load_data(user_id)

    if any(account["steamid"] == steamid64 for account in data["tracked_accounts"]):
        await update.message.reply_text(f"ℹ️ The account with SteamID64 `{steamid64}` is already being tracked.")
        return

    data["tracked_accounts"].append({"steamid": steamid64, "last_checked_ban": "Unknown"})
    save_data(user_id, data)

    await update.message.reply_text(f"✅ The account with SteamID64 `{steamid64}` has been successfully added to your tracked accounts.")