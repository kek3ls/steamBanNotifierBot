import json
import os
import httpx
from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode
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
        return {"tracked_accounts": [], "interval_hours": 6}

# Save data to a user-specific JSON file
def save_data(user_id, data):
    file_path = get_user_file(user_id)
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

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

# Async function to check the ban status
async def check_ban_status(steamid64):
    url = f"https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={STEAM_API_KEY}&steamids={steamid64}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                if "players" in data and len(data["players"]) > 0:
                    player_data = data["players"][0]

                    # Extract ban details
                    vac_banned = player_data.get("VACBanned", False)
                    community_banned = player_data.get("CommunityBanned", False)
                    economy_ban = player_data.get("EconomyBan", "none")
                    limited_account = player_data.get("LimitedAccount", False)
                    number_of_game_bans = player_data.get("NumberOfGameBans", 0)

                    # Create ban message
                    ban_state = []
                    if vac_banned:
                        ban_state.append("✅ VAC")
                    if community_banned:
                        ban_state.append("✅ Community")
                    if economy_ban != "none":
                        ban_state.append(f"💵 Economy Ban: {economy_ban}")
                    if limited_account:
                        ban_state.append("🔞 Limited Account")
                    if number_of_game_bans > 0:
                        ban_state.append(f"✅ Game Bans: {number_of_game_bans}")

                    return ", ".join(ban_state) if ban_state else None

    except Exception as e:
        return f"Error checking ban state for SteamID64 {steamid64}: {e}"

async def flush(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id  # Get the user's Telegram ID

    # Extract the user's credentials from the Telegram update
    telegram_user_data = extract_telegram_user_data(update.message.from_user)

    # Update the user's credentials in the JSON file
    update_user_credentials(user_id, telegram_user_data)

    data = load_data(user_id)  # Load only this user's tracked accounts

    if not data["tracked_accounts"]:
        await update.message.reply_text("❌ No tracked accounts found!")
        return

    response_message = "🔄 Checking the ban state for your tracked accounts:\n\n"
    banned_found = False  # Flag to track bans

    for account in data["tracked_accounts"]:
        steamid64 = account["steamid"]
        nickname = await get_player_nickname(steamid64)
        display_name = nickname if nickname else steamid64

        try:
            ban_state = await check_ban_status(steamid64)

            if ban_state:
                banned_found = True
                steam_profile_url = f"https://steamcommunity.com/profiles/{steamid64}"
                response_message += f"<a href='{steam_profile_url}'>{display_name}</a>: {ban_state}\n"
            else:
                steam_profile_url = f"https://steamcommunity.com/profiles/{steamid64}"
                response_message += f"<a href='{steam_profile_url}'>{display_name}</a>: No ban found\n"

        except Exception as e:
            response_message += f"Error checking ban for SteamID {steamid64}: {e}\n"

    if not banned_found:
        response_message = "❌ No banned accounts found!"

    await update.message.reply_text(response_message, parse_mode=ParseMode.HTML)