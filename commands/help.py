from telegram import Update
from telegram.ext import CallbackContext
from utils.save_credentials import update_user_credentials, extract_telegram_user_data

async def help_command(update: Update, context: CallbackContext) -> None:
	# Extract user data and update credentials
	user_id = update.message.from_user.id
	telegram_user_data = extract_telegram_user_data(update.message.from_user)
	
	# Update the user's credentials in the JSON file
	update_user_credentials(user_id, telegram_user_data)
	
	await update.message.reply_text(
		"📌 **Available Commands**:\n\n"

		"/start - Initiate the bot.\n"
		"/help - Display this help message.\n"
		"/add - Add a Steam account to be tracked.\n"
		"/flush - Check for bans on tracked accounts.\n"
		"/remove - Remove a Steam account from tracking.\n"
		"/list - View all currently tracked accounts.\n"
		"/startbancheck - Begin automatic ban checks every 6 hours.\n"
		"/stopbancheck - Halt the automatic ban check service.\n",
		# "/setinterval <hours> - Change check interval\n"
		# "/status - Show current check settings\n",
		parse_mode="Markdown"
	)