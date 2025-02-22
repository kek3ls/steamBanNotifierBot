import os
import asyncio
from telegram import Bot
from telegram.constants import ParseMode
from utils.data_editor import save_data, load_data
from utils.steam_api import check_ban_status, get_player_nickname

async def periodic_ban_check(bot: Bot, user_id: int):
	"""Checks the ban status of tracked accounts periodically and sends notifications to users."""
	while True:
		if not os.path.exists("user_data"):
			print(f"[DBG] Creating 'user_data' directory.")
			os.makedirs("user_data")

		for filename in os.listdir("user_data"):
			if filename.endswith(".json"):
				current_user_id = int(filename.split(".json")[0])  # Extract user ID
				print(f"[DBG] Processing user data for user_id: {current_user_id}")
				data = load_data(current_user_id)

				for account in data["trackedAccounts"]:
					steamid64 = account["steamid"]
					ban_notified = account.get("ban_notified", False)

					# Check the ban status if not notified yet
					if not ban_notified:
						print(f"[DBG] Checking ban status for SteamID64: {steamid64}")
						ban_state = await check_ban_status(steamid64)

						# If there is a ban status, update the 'isBanned' field and notify the user
						if ban_state:
							print(f"[INF] Ban state for SteamID64 {steamid64}: {ban_state}")
							nickname = await get_player_nickname(steamid64)
							display_name = nickname if nickname else steamid64
							steam_profile_url = f"https://steamcommunity.com/profiles/{steamid64}"
							message = f"🚨 <a href='{steam_profile_url}'>{display_name}</a> has been banned: {ban_state}"

							print(f"[INF] Sending ban notification to user {current_user_id}.")
							await bot.send_message(chat_id=current_user_id, text=message, parse_mode=ParseMode.HTML)

							# Override the 'isBanned' field with the current ban status
							account["isBanned"] = ban_state

							# Mark as notified for this user
							account["ban_notified"] = True
							save_data(current_user_id, data)
							print(f"[INF] Ban notification sent and status updated for {steamid64}.")

				# Fetch interval_hours from data or default to 6 hours if not provided
				interval_hours = data.get("interval_hours", 6)
				print(f"[DBG] Next check interval: {interval_hours} hours.")

		await asyncio.sleep(interval_hours * 3600)  # Sleep for the defined interval in seconds
		print(f"[DBG] Sleeping for {interval_hours * 3600} seconds.")