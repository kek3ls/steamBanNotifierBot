import asyncio
import os
from telegram.constants import ParseMode
from telegram import Bot
from utils.steam_api import check_ban_status, get_player_nickname
from utils.data_editor import save_data, load_data

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