from telegram import Update
from utils.data_editor import load_data
from telegram.ext import CallbackContext

async def list_accounts(update: Update, context: CallbackContext) -> None:
	user_id = update.message.from_user.id  # Get the user's Telegram ID

	print(f"[DBG] list_accounts command received for user_id: {user_id}")

	data = load_data(user_id)  # Load the tracked accounts for this user

	if not data["trackedAccounts"]:
		print(f"[WRN] No tracked accounts found for user_id: {user_id}")
		await update.message.reply_text("ℹ️ You are not currently tracking any Steam accounts.")
		return

	message = "📋 <b>Your Tracked Steam Accounts:</b>\nClick the SteamID to view the profile.\n\n"

	for account in data["trackedAccounts"]:
		steamid64 = account.get('steamid', None)
		nickname = account.get('nickname', None)

		# Display nickname if found, otherwise display SteamID64
		if nickname:
			print(f"[INF] Found nickname {nickname} for SteamID64: {steamid64}")
			message += f"🔹 {nickname} (<a href='https://steamcommunity.com/profiles/{steamid64}'>{steamid64}</a>)\n"
		else:
			print(f"[WRN] No nickname found for SteamID64: {steamid64}")
			message += f"🔹 <a href='https://steamcommunity.com/profiles/{steamid64}'>{steamid64}</a>\n"

	# Send the formatted message with HTML parsing enabled
	print(f"[INF] Sending list of tracked accounts to user_id: {user_id}")
	await update.message.reply_text(message, parse_mode="HTML")