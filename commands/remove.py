from utils.buttons import new_button
from commands.cancel import cancel
from telegram.ext import CallbackContext
from utils.message_handler import handle_message
from telegram import Update, InlineKeyboardMarkup
from utils.data_editor import save_data, load_data
from utils.steam_api import to_steamid64, get_player_nickname

async def remove(update: Update, context: CallbackContext) -> None:
	user_id = update.message.from_user.id  # Get the user's Telegram ID
	print(f"[DBG] remove command received for user_id: {user_id}")

	if context.user_data.get("WAITING_FOR_ACCOUNT_2_ADD", False):
		return

	# If user provided an argument (Steam account or 'all')
	if context.args:
		return await process_account(update, context, context.args[0])

	# If no account provided, ask for the account
	print(f"[WRN] No Steam account input provided by user_id: {user_id}")
	cancel_button = new_button("Cancel", cancel, user_id)
	keyboard = InlineKeyboardMarkup([[cancel_button]])

	await update.message.reply_text(
		"⚠️ Oops! You need to provide a valid Steam account input.\n\n"
		"Please send it now so we can remove it from your tracked accounts.",
		parse_mode="HTML",
		reply_markup=keyboard
	)

	# Store waiting state
	context.user_data["WAITING_FOR_ACCOUNT_2_REMOVE"] = True

async def remove_all_accounts(update: Update, context: CallbackContext):
	"""Handles the removal of all tracked accounts."""
	user_id = update.message.from_user.id
	data = load_data(user_id)
	print(f"[DBG] Removing all tracked accounts for user_id: {user_id}")
	data["trackedAccounts"] = []  # Clear the tracked accounts
	save_data(user_id, data)

	await update.message.reply_text("✅ All tracked accounts have been successfully removed.", parse_mode="HTML")

	context.user_data["WAITING_FOR_ACCOUNT_2_REMOVE"] = False  # Reset state

async def process_account(update: Update, context: CallbackContext, account_input: str):
	"""Processes the provided Steam account and removes it from tracking."""
	user_id = update.message.from_user.id

	print("[ACC INPUT]" + account_input)

	# If user input is 'all', remove all tracked accounts
	if account_input.lower() == "all":
		return await remove_all_accounts(update, context)

	# Convert the provided Steam account input to SteamID64 using to_steamid64
	try:
		steam_id = await to_steamid64(account_input)
	except ValueError as e:
		# If to_steamid64 fails (e.g., invalid account input)
		await update.message.reply_text(f"❌ Invalid Steam account! Please try again.")
		context.user_data["WAITING_FOR_ACCOUNT_2_REMOVE"] = False  # Reset state
		return

	data = load_data(user_id)

	original_count = len(data["trackedAccounts"])
	# Remove the account from the tracking list
	data["trackedAccounts"] = [acc for acc in data["trackedAccounts"] if acc["steamid"] != steam_id]
	save_data(user_id, data)

	# Check if the account was found and removed
	nickname = await get_player_nickname(steam_id)
	profile_url = f"https://steamcommunity.com/profiles/{steam_id}"

	if len(data["trackedAccounts"]) < original_count:
		print(f"[INF] {nickname or steam_id} (SteamID: {steam_id}) removed from tracking for user_id: {user_id}")
		await update.message.reply_text(
			f"✅ {nickname or steam_id} has been successfully removed from tracking. "
			f"(<a href='{profile_url}'>{steam_id}</a>)",
			parse_mode="HTML"
		)
	else:
		print(f"[WRN] {nickname or steam_id} (SteamID: {steam_id}) not found in tracking list for user_id: {user_id}")
		await update.message.reply_text(
			f"⚠️ <a href='{profile_url}'>{steam_id}</a> was not found in your tracking list.",
			parse_mode="HTML"
		)

	context.user_data["WAITING_FOR_ACCOUNT_2_REMOVE"] = False  # Reset state

async def handle_waiting_account(update: Update, context: CallbackContext):
	if context.user_data.get("WAITING_FOR_ACCOUNT_2_ADD", False):
		return

	"""Handles the next message when waiting for a Steam account input."""
	if context.user_data.get("WAITING_FOR_ACCOUNT_2_REMOVE", False):  # Check if it's True
		await process_account(update, context, update.message.text)
		return

	# If not waiting, treat it as a normal message
	return await handle_message(update, context)