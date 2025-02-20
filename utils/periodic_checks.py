import json
import httpx
import asyncio
import os
from telegram.constants import ParseMode
from telegram import Bot
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
                    vac_banned = player_data.get("VACBanned", False)
                    community_banned = player_data.get("CommunityBanned", False)
                    economy_ban = player_data.get("EconomyBan", "none")
                    limited_account = player_data.get("LimitedAccount", False)
                    number_of_game_bans = player_data.get("NumberOfGameBans", 0)

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
    return None

async def periodic_ban_check(bot: Bot, user_id: int):
    # Now it can handle user_id as well
    while True:
        if not os.path.exists("user_data"):
            os.makedirs("user_data")

        for filename in os.listdir("user_data"):
            if filename.endswith(".json"):
                current_user_id = int(filename.split(".json")[0])  # Extract user ID
                data = load_data(current_user_id)

                for account in data["tracked_accounts"]:
                    steamid64 = account["steamid"]
                    ban_notified = account.get("ban_notified", False)

                    if not ban_notified:
                        ban_state = await check_ban_status(steamid64)
                        if ban_state:
                            nickname = await get_player_nickname(steamid64)
                            display_name = nickname if nickname else steamid64
                            steam_profile_url = f"https://steamcommunity.com/profiles/{steamid64}"
                            message = f"🚨 <a href='{steam_profile_url}'>{display_name}</a> has been banned: {ban_state}"

                            await bot.send_message(chat_id=current_user_id, text=message, parse_mode=ParseMode.HTML)

                            # Mark as notified for this user
                            account["ban_notified"] = True
                            save_data(current_user_id, data)

                interval_hours = data.get("interval_hours", 6)

        await asyncio.sleep(interval_hours * 3600)  # Sleep for the defined interval