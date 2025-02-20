from telegram import Update
from telegram.ext import CallbackContext
import os
import json
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
        return {"tracked_accounts": []}  # Default empty list for new users

# Save data to a user-specific JSON file
def save_data(user_id, data):
    file_path = get_user_file(user_id)
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

async def remove(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id  # Get the user's Telegram ID

    # Extract the user's credentials from the Telegram update
    telegram_user_data = extract_telegram_user_data(update.message.from_user)

    # Update the user's credentials in the JSON file
    update_user_credentials(user_id, telegram_user_data)
    
    if len(context.args) == 0:
        await update.message.reply_text(
            "❌ Please provide a SteamID to remove.\nExample: `/remove 12345678901234567`",
            parse_mode="Markdown"
        )
        return

    steam_id = context.args[0]
    data = load_data(user_id)  # Load only this user's tracked accounts

    if steam_id.lower() == "all":
        data["tracked_accounts"] = []
        save_data(user_id, data)
        await update.message.reply_text("✅ All tracked accounts have been removed.", parse_mode="Markdown")
    else:
        original_count = len(data["tracked_accounts"])
        data["tracked_accounts"] = [acc for acc in data["tracked_accounts"] if acc["steamid"] != steam_id]
        save_data(user_id, data)

        if len(data["tracked_accounts"]) < original_count:
            await update.message.reply_text(f"✅ Removed SteamID `{steam_id}` from tracking.", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"⚠️ SteamID `{steam_id}` not found in your tracking list.", parse_mode="Markdown")