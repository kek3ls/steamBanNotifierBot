from utils.buttons import new_button
from utils.logger import debug_print
from telegram.ext import CallbackContext
from utils.steam_api import to_steamid64
from utils.steam_api import check_ban_status
from telegram import Update, InlineKeyboardMarkup
from utils.data_editor import save_data, load_data
from utils.steam_api import get_account_summary, write_account_summary

async def add_command(update: Update, context: CallbackContext):
	from commands.remove import accountWaiting as waitingForAccount2Remove
	from commands.cancel import handle_cancel_button

	userid = update.message.from_user.id

	debug_print("debug", f"add command requested by {userid}")

	buttons = [
		[  # Each [] is new row
			new_button("❌ Cancel", handle_cancel_button, "cancel")
		]
	]

	if await accountWaiting(userid) or await waitingForAccount2Remove(userid):
		return await update.message.reply_text(
			"✋ You have an ongoing action, please /<b>cancel</b> it first.",
			parse_mode="HTML",
			reply_markup=InlineKeyboardMarkup(buttons)
		)

	data = await load_data(userid)

	if len(data["trackedAccounts"]) >= 10:
		await update.message.reply_text("⚠️ You\'ve reached the maximum limit of tracked accounts! (10)", parse_mode="HTML")
		return

	# If user provided an argument, process it immediately
	if context.args:
		await accountWaiting(userid, False)
		return await process_account(update, context, context.args[0])

	# No account provided, ask user for input
	debug_print("info", f"No Steam account input provided by {userid}")
	await update.message.reply_text(
		"❗ Oops! You need to provide a valid Steam account input.\n\n"
		"Please send it now so it can be added into your tracked accounts.\n\n",
		parse_mode="HTML",
		reply_markup=InlineKeyboardMarkup(buttons)
	)

	await accountWaiting(userid, True)

async def process_account(update: Update, context: CallbackContext, input: str):
	userid = update.message.from_user.id
	steamid64 = await to_steamid64(input)

	if not steamid64:
		await update.message.reply_text("❌ Invalid Steam account! Please try again.")
		await accountWaiting(userid, False)  # Reset state
		return

	sent_message = await update.message.reply_text(
		"🔄 Fetching information.\n\n"
		"This is a <b>very heavy</b> process, be patient!\n\n"
		"If you wish to see what information we collect during adding process, "
		"you can follow this link: <a href='https://sample.com/'><b>click</b></a>",
		parse_mode="HTML"
	)

	debug_print("debug", f"Converted Steam account input to {steamid64}")

	data = await load_data(userid)

	if len(data["trackedAccounts"]) >= 10:
		await sent_message.edit_text("⚠️ You\'ve reached the maximum limit of tracked accounts! (10)", parse_mode="HTML")
		await accountWaiting(userid, False)  # Reset state
		return

	# Check if the account is already being tracked
	if any(account["steamid"] == steamid64 for account in data["trackedAccounts"]):
		await sent_message.edit_text("🔁 This account is already being tracked!", parse_mode="HTML")
		await accountWaiting(userid, False)  # Reset state
		return

	# Fetch player summary details
	player_summary = await get_account_summary(steamid64)

	if player_summary is None:
		await sent_message.edit_text("❌ Unable to fetch Steam account details! Please try again.", parse_mode="HTML")
		await accountWaiting(userid, False)  # Reset state
		return

	await write_account_summary(userid, steamid64, True)

	debug_print("info", f"Added {steamid64} to tracking for {userid}")

	# Check ban status after adding the account
	ban_status = await check_ban_status(userid, steamid64)

	# Inform the user about the added account and its ban status
	await sent_message.edit_text(
		f"✅ Success! {player_summary['nickname']} "
		f"(<a href='{player_summary['profileURL']}'>{steamid64}</a>) "
		f"has been added to your tracked accounts.\n\n"
		f"Ban status: {ban_status or 'No bans detected'}\n\n"
		"✨ You can use /<b>startbancheck</b> or /<b>startbc</b> to get notifications if any of your tracked accounts gets banned.",
		parse_mode="HTML"
	)

	await accountWaiting(userid, False)

async def accountWaiting(userid:int, state: bool = None):
	data = await load_data(userid)

	# isWaitingForAccount2Add = str(data["globals"]["isWaitingForAccount2Add"])

	if state is None:
		# debug_print('info', f"isWaitingForAccount2Add == " + isWaitingForAccount2Add)
		return data["globals"]["isWaitingForAccount2Add"]
	else:
		# debug_print('info', f"isWaitingForAccount2Add = {state}")
		data["globals"]["isWaitingForAccount2Add"] = state
		await save_data(userid, data)