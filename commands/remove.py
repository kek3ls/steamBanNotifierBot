from telegram import Update
from telegram.ext import CallbackContext
from utils.constants import WAITING_FOR_ACCOUNT
from utils.message_handler import handle_message
from utils.data_editor import save_data, load_data
from utils.steam_api import to_steamid64, get_player_nickname
from utils.telegram_credentials import get as get_credentials
from utils.telegram_credentials import write as write_credentials

async def remove(update: Update, context: CallbackContext) -> None:
	"""Handles the /remove command, waiting for a Steam account if not provided."""
	user_id = update.message.from_user.id  # Get the user's Telegram ID

	print(f"[DBG] remove command received for user_id: {user_id}")

	# Update user's credentials in the JSON file
	print(f"[DBG] Writing credentials for user_id: {user_id}")
	write_credentials(user_id, get_credentials(update.message.from_user))

	# If user provided an argument (Steam account or 'all')
	if context.args:
		return await process_remove_account(update, context, context.args[0])

	# If no account provided, ask for the account
	print(f"[WRN] No Steam account input provided by user_id: {user_id}")
	await update.message.reply_text(
		"⚠️ Oops! You need to provide a valid Steam account input.\n\n"
		"Please send it now so we can remove it from your tracked accounts.\n\n"
		"🛑 If you want to cancel, use /cancel."
	)

	# Store waiting state
	context.user_data[WAITING_FOR_ACCOUNT] = True

async def process_remove_account(update: Update, context: CallbackContext, account_input: str):
	"""Processes the provided Steam account and removes it from tracking."""
	user_id = update.message.from_user.id

	# If user input is 'all', remove all tracked accounts
	if account_input.lower() == "all":
		return await remove_all_accounts(update, context)

	# Convert the provided Steam account input to SteamID64 using to_steamid64
	try:
		steam_id = await to_steamid64(account_input)
	except ValueError as e:
		# If to_steamid64 fails (e.g., invalid account input)
		await update.message.reply_text(f"❌ Invalid Steam account input. {str(e)} Operation cancelled.")
		context.user_data.pop(WAITING_FOR_ACCOUNT, None)  # Reset state
		return

	data = load_data(user_id)

	original_count = len(data["trackedAccounts"])
	# Remove the account from the tracking list
	data["trackedAccounts"] = [acc for acc in data["trackedAccounts"] if acc["steamid"] != steam_id]
	save_data(user_id, data)

	# Check if the account was found and removed
	nickname = await get_player_nickname(steam_id)
	if nickname:
		profile_url = f"https://steamcommunity.com/profiles/{steam_id}"

	if len(data["trackedAccounts"]) < original_count:
		print(f"[INF] {nickname} (SteamID: {steam_id}) removed from tracking for user_id: {user_id}")
		await update.message.reply_text(
			f"✅ {nickname} has been successfully removed from tracking. "
			f"(<a href='{profile_url}'>{steam_id}</a>)",
			parse_mode="HTML"
		)
	else:
		print(f"[WRN] {nickname} (SteamID: {steam_id}) not found in tracking list for user_id: {user_id}")
		await update.message.reply_text(
			f"⚠️ {nickname} (<a href='https://steamcommunity.com/profiles/{steam_id}'>{steam_id}</a>) "
			"was not found in your tracking list.",
			parse_mode="HTML"
		)

	context.user_data.pop(WAITING_FOR_ACCOUNT, None)  # Reset state

async def remove_all_accounts(update: Update, context: CallbackContext):
	"""Handles the removal of all tracked accounts."""
	user_id = update.message.from_user.id
	data = load_data(user_id)
	print(f"[DBG] Removing all tracked accounts for user_id: {user_id}")
	data["trackedAccounts"] = []  # Clear the tracked accounts
	save_data(user_id, data)

	await update.message.reply_text("✅ All tracked accounts have been successfully removed.", parse_mode="Markdown")

	context.user_data.pop(WAITING_FOR_ACCOUNT, None)  # Reset state

async def handle_waiting_account(update: Update, context: CallbackContext):
	"""Handles the next message when waiting for a Steam account input."""
	if context.user_data.get(WAITING_FOR_ACCOUNT):
		return await process_remove_account(update, context, update.message.text)

	# If not waiting, treat it as a normal message
	return await handle_message(update, context)