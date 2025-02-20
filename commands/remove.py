from telegram import Update
from telegram.ext import CallbackContext
from utils.steam_api import get_player_nickname
from utils.data_editor import save_data, load_data
from utils.steamid_conversion import convert_to_steamid64
from utils.save_credentials import update_user_credentials, extract_telegram_user_data

async def remove(update: Update, context: CallbackContext) -> None:
	user_id = update.message.from_user.id  # Get the user's Telegram ID

	# Extract the user's credentials from the Telegram update
	telegram_user_data = extract_telegram_user_data(update.message.from_user)

	# Update the user's credentials in the JSON file
	update_user_credentials(user_id, telegram_user_data)
	
	if len(context.args) == 0:
		await update.message.reply_text(
			"❌ You must provide a valid Steam account input.\n\n"
			"I accept the following formats:\n"
			"- SteamID64 (12345678901234567)\n"
			"- Steam profile URL (https://steamcommunity.com/profiles/12345678901234567)\n"
			"- Steam custom profile URL (https://steamcommunity.com/id/xxx)\n"
			"- SteamID3 ([U:1:12345678])\n"
			"- Steam shortened URL (https://s.team/p/abcd-dcba)"
		)
		return

	data = load_data(user_id)  # Load only this user's tracked accounts

	if context.args == "all":
		data["tracked_accounts"] = []
		save_data(user_id, data)
		await update.message.reply_text("✅ All tracked accounts have been successfully removed.", parse_mode="Markdown")
	else:
		steam_id = await convert_to_steamid64(context.args[0])

		original_count = len(data["tracked_accounts"])
		data["tracked_accounts"] = [acc for acc in data["tracked_accounts"] if acc["steamid"] != steam_id]
		save_data(user_id, data)

		nickname = await get_player_nickname(steam_id)

		if len(data["tracked_accounts"]) < original_count:
			await update.message.reply_text(
				f"✅ {nickname} has been removed from tracking. "
				f"(<a href='https://steamcommunity.com/profiles/{steam_id}'>{steam_id}</a>)",
				parse_mode="HTML"
			)
		else:
			await update.message.reply_text(
				f"⚠️ {nickname} (<a href='https://steamcommunity.com/profiles/{steam_id}'>{steam_id}</a>) "
				"is not found in your tracking list.",
				parse_mode="HTML"
			)