from telegram import Update
from utils.logger import debug_print
from utils.data_editor import load_data
from telegram.ext import CallbackContext
from utils.steam_api import get_nickname

async def list_command(update: Update, context: CallbackContext) -> None:
	userid = update.message.from_user.id

	debug_print("debug", f"list command requested by {userid}")

	sent_message = await update.message.reply_text("🔄 Fetching information, please wait.", parse_mode="HTML")

	data = await load_data(userid)

	if not data:
		await update.message.reply_text("⚠️ There was an error loading your accounts, please try again later!" \
			"If you suspect a problem, use /<b>data</b> to review or delete your file.",
			parse_mode="HTML"
		)
		return

	if not data["trackedAccounts"]:
		debug_print("info", f"no tracked accounts found for {userid}")
		await sent_message.edit_text(
			"ℹ️ You are not currently tracking any Steam accounts, or there was an issue loading your data." \
			"If you suspect a problem, use /<b>data</b> to review or delete your file.",
			parse_mode="HTML"
		)
		return

	message_list = ["📋 <b>Your tracked steam accounts</b>:\nClick the SteamID to view the profile.\n"]

	for account in data["trackedAccounts"]:
		steamid64 = account.get("steamid", None)

		if not steamid64:
			message_list.append(f"⚠️ unknown (There was an error parsing the SteamID64, try again later, please!)")
			continue

		display_name = await get_nickname(steamid64, userid)

		# Display nickname if found, otherwise display SteamID64
		if display_name:
			message_list.append(f"🔹 {display_name} (<a href='https://steamcommunity.com/profiles/{steamid64}'>{steamid64}</a>)")
		else:
			message_list.append(f"🔹 <a href='https://steamcommunity.com/profiles/{steamid64}'>{steamid64}</a>")

	# Join list into a single string
	message = "\n".join(message_list)

	# Edit the previously sent message with the account list
	debug_print("info", f"Sending list of tracked accounts to {userid}")
	await sent_message.edit_text(message, parse_mode="HTML")