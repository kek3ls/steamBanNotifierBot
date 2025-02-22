from telegram import Update
from utils.data_editor import load_data
from telegram.ext import CallbackContext
from telegram.constants import ParseMode
from utils.telegram_credentials import get as get_credentials
from utils.telegram_credentials import write as write_credentials
from utils.steam_api import check_ban_status, get_player_nickname, to_steamid64

async def flush(update: Update, context: CallbackContext):
	user_id = update.message.from_user.id  # Get the user's Telegram ID

	print(f"[DBG] flush command received from user_id: {user_id}")

	# Update the user's credentials in the JSON file
	print(f"[DBG] Writing credentials for user_id: {user_id}")
	write_credentials(user_id, get_credentials(update.message.from_user))

	data = load_data(user_id)  # Load only this user's tracked accounts

	if not data["trackedAccounts"]:
		print(f"[WRN] No tracked accounts found for user_id: {user_id}")
		await update.message.reply_text("❌ You don't have any tracked accounts yet!")
		return

	await update.message.reply_text("🔄 Checking the ban status for your tracked accounts.", parse_mode=ParseMode.HTML)

	banned_found = False  # Flag to track if any bans are found

	response_message = ""

	for account in data["trackedAccounts"]:
		# Convert SteamID from various formats (URL, SteamID3, etc.) to SteamID64
		steamid64 = await to_steamid64(account["steamid"])

		if not steamid64:
			response_message += f"⚠️ Invalid Steam account format: {account['steamid']}\n"
			continue

		# Fetch the nickname or display name of the account
		nickname = account.get('nickname', None)
		display_name = nickname if nickname else steamid64

		try:
			ban_state = await check_ban_status(user_id, steamid64)

			if ban_state:
				banned_found = True
				steam_profile_url = f"https://steamcommunity.com/profiles/{steamid64}"
				response_message += f"<a href='{steam_profile_url}'>{display_name}</a>: {ban_state}\n"
			else:
				steam_profile_url = f"https://steamcommunity.com/profiles/{steamid64}"
				response_message += f"<a href='{steam_profile_url}'>{display_name}</a>: No ban found\n"

		except Exception as e:
			print(f"[ERR] Error checking ban for SteamID {steamid64}: {e}")
			response_message += f"⚠️ Error checking ban for <a href='https://steamcommunity.com/profiles/{steamid64}'>SteamID {steamid64}</a>: {e}\n"

	if not banned_found:
		response_message = "❌ No banned accounts found in your tracked list."
		print(f"[INF] No banned accounts found for user_id: {user_id}")

	print(f"[INF] Sending ban status response to user_id: {user_id}")
	await update.message.reply_text(response_message, parse_mode=ParseMode.HTML)