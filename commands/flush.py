from telegram import Update
from utils.logger import debug_print
from utils.data_editor import load_data
from telegram.ext import CallbackContext
from utils.steam_api import check_ban_status, get_nickname, write_account_summary

async def flush_command(update: Update, context: CallbackContext):
	userid = update.message.from_user.id

	debug_print("debug", f"flush command requested by {userid}")

	sent_message = await update.message.reply_text("🔄 Fetching ban information.\n\n" \
		"This is a heavy process, be patient!", parse_mode="HTML")

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

	banned_found = False

	message_list = ["📋 <b>Your tracked steam accounts</b>:\nClick the SteamID to view the profile.\n"]

	for account in data["trackedAccounts"]:
		steamid64 = account["steamid"]

		if not steamid64:
			message_list.append(f"⚠️ unknown (There was an error parsing the SteamID64, try again later, please!)")
			continue

		await write_account_summary(userid, steamid64)
		display_name = await get_nickname(steamid64, userid)

		try:
			ban_state = await check_ban_status(userid, steamid64)

			if not ban_state:
				ban_state = "❌ No bans found!"
			else:
				banned_found = True
				ban_state = "✅ " + ban_state

			steam_profile_url = f"https://steamcommunity.com/profiles/{steamid64}"

			if display_name:
				message_list.append(f"{display_name} (<a href='{steam_profile_url}'>{steamid64}</a>): {ban_state}\n")
			else:
				message_list.append(f"<a href='{steam_profile_url}'>{steamid64}</a>: {ban_state}\n")
		except Exception as e:
			debug_print("error", f"Error checking ban for SteamID {steamid64}: {e}")

			if display_name:
				message_list.append(f"{display_name} (<a href='https://steamcommunity.com/profiles/{steamid64}'>{steamid64}</a>) ⚠️ There was an error, try again later!\n")
			else:
				message_list.append(f"<a href='https://steamcommunity.com/profiles/{steamid64}'>{steamid64}</a> ⚠️ There was an error, try again later!\n")

	message = "\n".join(message_list)

	if not banned_found:
		debug_print("info", f"no banned accounts found for {userid}")
		message = "❌ No banned accounts found in your tracking accounts."

	debug_print("info", f"Sending ban status response to {userid}")
	await sent_message.edit_text(message, parse_mode="HTML")