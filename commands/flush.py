from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode
from utils.save_credentials import update_user_credentials, extract_telegram_user_data
from utils.steam_api import check_ban_status, get_player_nickname
from utils.data_editor import load_data

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

	response_message = "🔄 Checking the ban status for your tracked accounts:\n\n"
	banned_found = False  # Flag to track if any bans are found

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
		response_message = "❌ No banned accounts found."

	await update.message.reply_text(response_message, parse_mode=ParseMode.HTML)