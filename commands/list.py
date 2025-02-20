from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode
from utils.data_editor import load_data
from utils.steam_api import get_player_nickname
from utils.save_credentials import update_user_credentials, extract_telegram_user_data

async def list_accounts(update: Update, context: CallbackContext) -> None:
	user_id = update.message.from_user.id  # Get the user's Telegram ID

	# Extract the user's credentials from the Telegram update
	telegram_user_data = extract_telegram_user_data(update.message.from_user)

	# Update the user's credentials in the JSON file
	update_user_credentials(user_id, telegram_user_data)

	data = load_data(user_id)  # Load the tracked accounts for this user

	if not data["tracked_accounts"]:
		await update.message.reply_text("ℹ️ You are not currently tracking any Steam accounts.")
		return

	message = "📋 <b>Your Tracked Steam Accounts:</b>\nClick the SteamID to view the profile.\n\n"

	for account in data["tracked_accounts"]:
		steamid64 = account["steamid"]
		nickname = await get_player_nickname(steamid64)

		# Display nickname if found, otherwise display SteamID64
		if nickname:
			message += f"🔹 {nickname} (<a href='https://steamcommunity.com/profiles/{steamid64}'>{steamid64}</a>)\n"
		else:
			message += f"🔹 <a href='https://steamcommunity.com/profiles/{steamid64}'>{steamid64}</a>\n"

	# Send the formatted message with HTML parsing enabled
	await update.message.reply_text(message, parse_mode=ParseMode.HTML)