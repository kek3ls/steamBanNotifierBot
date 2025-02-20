import os
import json
import httpx
from telegram.constants import ParseMode  
from telegram import Update
from telegram.ext import CallbackContext
from utils.save_credentials import update_user_credentials, extract_telegram_user_data
from utils.load_api_keys import STEAM_API_KEY

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

# Async function to get the player's nickname
async def get_player_nickname(steamid64):
    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={STEAM_API_KEY}&steamids={steamid64}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                if "response" in data and "players" in data["response"]:
                    players = data["response"]["players"]
                    if players:
                        return players[0].get("personaname", None)

    except Exception as e:
        print(f"Error fetching nickname for SteamID64 {steamid64}: {e}")
    return None


async def list_accounts(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id  # Get the user's Telegram ID

    # Extract the user's credentials from the Telegram update
    telegram_user_data = extract_telegram_user_data(update.message.from_user)

    # Update the user's credentials in the JSON file
    update_user_credentials(user_id, telegram_user_data)

    data = load_data(user_id)  # Load only this user's tracked accounts

    if not data["tracked_accounts"]:
        await update.message.reply_text("ℹ️ You are not tracking any Steam accounts.")
        return

    message = "📋 Your Tracked Steam Accounts:\nClick the SteamID to open the profile.\n\n"

    for account in data["tracked_accounts"]:
        steamid64 = account["steamid"]
        nickname = await get_player_nickname(steamid64)

        # Use the nickname if found, otherwise just display the SteamID64
        if nickname:
            message += f"🔹 {nickname} (<a href='https://steamcommunity.com/profiles/{steamid64}'>{steamid64}</a>)\n"
        else:
            message += f"🔹 <a href='https://steamcommunity.com/profiles/{steamid64}'>{steamid64}</a>\n"

    # Send the response back with HTML parsing enabled
    await update.message.reply_text(message, parse_mode=ParseMode.HTML)