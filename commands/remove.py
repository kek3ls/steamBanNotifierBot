from utils.buttons import new_button
from utils.logger import debug_print
from telegram.ext import CallbackContext
from telegram import Update, InlineKeyboardMarkup
from utils.data_editor import save_data, load_data
from utils.steam_api import to_steamid64, get_nickname

async def remove_command(update: Update, context: CallbackContext) -> None:
	from commands.add import accountWaiting as waitingForAccount2Add
	from commands.cancel import handle_cancel_button

	userid = update.message.from_user.id
	
	debug_print("debug", f"remove command requested by {userid}")

	buttons = [
		[  # Each [] is new row
			new_button("❌ Cancel", handle_cancel_button, "cancel")
		]
	]

	if await accountWaiting(userid) or await waitingForAccount2Add(userid):
		return await update.message.reply_text(
			"✋ You have an ongoing action, please /<b>cancel</b> it first.",
			parse_mode="HTML",
			reply_markup=InlineKeyboardMarkup(buttons)
		)

	if context.args:
		return await process_remove_account(update, context, context.args[0])

	# If no account provided, ask for the account
	debug_print("info", f"no steam account input provided by {userid}")
	await update.message.reply_text(
		"❗ Oops! You need to provide a valid Steam account input.\n\n"
		"Please send it now so it can be removed from your tracked accounts.\n\n",
		parse_mode="HTML",
		reply_markup=InlineKeyboardMarkup(buttons)
	)

	# Store waiting state
	await accountWaiting(userid, True)

async def process_remove_account(update: Update, context: CallbackContext, account_input: str):
	userid = update.message.from_user.id

	# If user input is 'all', remove all tracked accounts
	if account_input.lower() == "all":
		return await remove_all_accounts(update, context)

	steamid64 = await to_steamid64(input)

	if not steamid64:
		await update.message.reply_text("❌ Invalid Steam account! Please try again.")
		await accountWaiting(userid, False)  # Reset state
		return

	data = await load_data(userid)

	if not data:
		await update.message.reply_text("⚠️ There was an error loading your accounts, please try again later!" \
			"If you suspect a problem, use /<b>data</b> to review or delete your file.",
			parse_mode="HTML"
		)
		return
	
	if not data["trackedAccounts"]:
		debug_print("info", f"no tracked accounts found for {userid}")
		await update.message.reply_text(
			"ℹ️ You are not currently tracking any Steam accounts, or there was an issue loading your data." \
			"If you suspect a problem, use /<b>data</b> to review or delete your file.",
			parse_mode="HTML"
		)
		return

	original_count = len(data["trackedAccounts"])

	data["trackedAccounts"] = [acc for acc in data["trackedAccounts"] if acc["steamid"] != steamid64]
	await save_data(userid, data)

	# Check if the account was found and removed
	nickname = await get_nickname(steamid64, userid)
	profile_url = f"https://steamcommunity.com/profiles/{steamid64}"

	if len(data["trackedAccounts"]) < original_count:
		debug_print("info", f"{steamid64} is removed from tracked accounts for {userid}")

		await update.message.reply_text(
			f"✅ {nickname} (<a href='{profile_url}'>{steamid64}</a>)\n" \
			"has been successfully removed from tracked accounts.",
			parse_mode="HTML"
		)
	else:
		debug_print("warning", f"{steamid64} is not found in tracked accounts for {userid}")

		await update.message.reply_text(
			f"⚠️ {nickname} (<a href='https://steamcommunity.com/profiles/{steamid64}'>{steamid64}</a>) " \
			"was not found in your tracked accounts.",
			parse_mode="HTML"
		)

	await accountWaiting(update.message.from_user.id, False)  # Reset state

async def remove_all_accounts(update: Update, context: CallbackContext):
	"""Handles the removal of all tracked accounts."""
	userid = update.message.from_user.id
	debug_print("debug", f"removing all tracked accounts for {userid}")

	data = await load_data(userid)

	if not data:
		await update.message.reply_text("⚠️ There was an error loading your accounts, please try again later!" \
			"If you suspect a problem, use /<b>data</b> to review or delete your file.",
			parse_mode="HTML"
		)
		return
	
	if not data["trackedAccounts"]:
		debug_print("info", f"no tracked accounts found for {userid}")
		await update.message.reply_text(
			"ℹ️ You are not currently tracking any Steam accounts, or there was an issue loading your data." \
			"If you suspect a problem, use /<b>data</b> to review or delete your file.",
			parse_mode="HTML"
		)
		return

	data["trackedAccounts"] = []
	await save_data(userid, data)

	await update.message.reply_text("✅ All tracked accounts have been successfully removed.", parse_mode="HTML")

	await accountWaiting(update.message.from_user.id, False)  # Reset state

async def accountWaiting(userid, state: bool = None):
	data = await load_data(userid)
	
	# isWaitingForAccount2Remove = str(data["globals"]["isWaitingForAccount2Remove"])

	if state is None:
		# debug_print('info', f"isWaitingForAccount2Remove == " + isWaitingForAccount2Remove)
		return data["globals"]["isWaitingForAccount2Remove"]
	else:
		# debug_print('info', f"isWaitingForAccount2Remove = {state}")
		data["globals"]["isWaitingForAccount2Remove"] = state
		await save_data(userid, data)