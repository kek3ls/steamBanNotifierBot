from commands.cancel import cancel
from utils.buttons import new_button
from telegram.ext import CallbackContext
from utils.steam_api import to_steamid64
from utils.steam_api import check_ban_status
from utils.steam_api import get_player_summary
from utils.message_handler import handle_message
from telegram import Update, InlineKeyboardMarkup
from utils.data_editor import save_data, load_data

async def add_account(update: Update, context: CallbackContext):
	user_id = update.message.from_user.id
	print(f"[DBG] add_account command received from user_id: {user_id}")

	if context.user_data.get("WAITING_FOR_ACCOUNT_2_REMOVE", False):
		return

	# If user provided an argument, process it immediately
	if context.args:
		return await process_account(update, context, context.args[0])

	# No account provided, ask user for input
	print(f"[WRN] No Steam account input provided by user_id: {user_id}")
	cancel_button = new_button("Cancel", cancel, user_id)
	keyboard = InlineKeyboardMarkup([[cancel_button]])

	await update.message.reply_text(
		"⚠️ Oops! You need to provide a valid Steam account input.\n\n"
		"Please send it now so we can add it to your tracked accounts.",
		parse_mode="HTML",
		reply_markup=keyboard
	)

	# Store waiting state
	context.user_data["WAITING_FOR_ACCOUNT_2_ADD"] = True

async def process_account(update: Update, context: CallbackContext, account_input: str):
	"""Processes the provided Steam account and adds it to tracking."""
	user_id = update.message.from_user.id
	steamid64 = await to_steamid64(account_input)

	if not steamid64:
		await update.message.reply_text("❌ Invalid Steam account! Please try again.")
		context.user_data["WAITING_FOR_ACCOUNT_2_ADD"] = True  # Reset state
		return

	print(f"[DBG] Converted Steam account input to SteamID64: {steamid64}")

	data = load_data(user_id)

	# Check if the account is already being tracked
	if any(account["steamid"] == steamid64 for account in data["trackedAccounts"]):
		await update.message.reply_text("🔁 This account is already being tracked!")
		context.user_data["WAITING_FOR_ACCOUNT_2_ADD"] = False  # Reset state
		return

	# Fetch player summary details
	player_summary = await get_player_summary(steamid64)
	if player_summary is None:
		await update.message.reply_text("❌ Unable to fetch Steam account details! Please send an account again.")
		context.user_data["WAITING_FOR_ACCOUNT_2_ADD"] = True  # Reset state
		return

	# Add account to the tracked list
	account_info = {
		"steamid": steamid64,
		"isBanned": "Unknown",
		"nickname": player_summary["nickname"],
		"url": player_summary["profile_url"],
		"avatar": player_summary["avatar"]
	}

	data["trackedAccounts"].append(account_info)
	save_data(user_id, data)

	print(f"[INF] Added SteamID64 {steamid64} to tracking for user_id: {user_id}")

	# Check ban status after adding the account
	ban_status = await check_ban_status(user_id, steamid64)

	# Update the 'isBanned' field in the tracked account
	for account in data["trackedAccounts"]:
		if account["steamid"] == steamid64:
			account["isBanned"] = False if ban_status == "No bans detected" else ban_status
			break

	# Save the updated data
	save_data(user_id, data)

	# Inform the user about the added account and its ban status
	await update.message.reply_text(
		f"✅ Success! {player_summary['nickname']} "
		f"(<a href='{player_summary['profile_url']}'>{steamid64}</a>) "
		f"has been added to your tracked accounts.\n\n"
		f"🛑 Ban status: {ban_status or 'No bans detected'}\n\n"
		"✨ You can use /startbancheck to get notifications if any of your tracked accounts gets banned.",
		parse_mode="HTML"
	)

	context.user_data["WAITING_FOR_ACCOUNT_2_ADD"] = False  # Reset state

async def handle_waiting_account(update: Update, context: CallbackContext):
	if context.user_data.get("WAITING_FOR_ACCOUNT_2_REMOVE", False):
		return

	"""Handles the next message when waiting for a Steam account input."""
	if context.user_data.get("WAITING_FOR_ACCOUNT_2_ADD", False):
		return await process_account(update, context, update.message.text)

	# If not waiting, treat it as a normal message
	return await handle_message(update, context)