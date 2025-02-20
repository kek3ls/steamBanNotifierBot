from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode
from utils.steam_api import get_player_nickname
from utils.data_editor import save_data, load_data
from utils.steamid_conversion import convert_to_steamid64
from utils.save_credentials import update_user_credentials, extract_telegram_user_data

async def add_account(update: Update, context: CallbackContext):
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

	input_str = context.args[0]
	steamid64 = await convert_to_steamid64(input_str)

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

	data = load_data(user_id)

	# Check if the account is already in the tracking list
	if any(account["steamid"] == steamid64 for account in data["tracked_accounts"]):
		await update.message.reply_text("ℹ️ This account is already in your tracking list.")
		return

	# Add the account to the tracking list
	data["tracked_accounts"].append({"steamid": steamid64, "last_checked_ban": "Unknown"})
	save_data(user_id, data)

	nickname = await get_player_nickname(steamid64)

	# Send confirmation message with the account added
	await update.message.reply_text(
		f"✅ {nickname} "
		f"(<a href='https://steamcommunity.com/profiles/{steamid64}'>{steamid64}</a>) "
		"has been successfully added to your tracked accounts.",
		parse_mode=ParseMode.HTML
	)