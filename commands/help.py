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
		"📌 *Available Commands:*\n\n"
		"/start - Start the bot.\n"
		"/help - Show this help message.\n"
		"/add - Add a steam account to tracing\n"
		"/flush - Check available accounts for bans.\n"
		"/remove - Remove an account from tracing.\n"
		"/list - List of all availables accounts.\n"
		"/startbancheck - Start the service to check bans each 6 hours.\n"
		"/stopbancheck - Stop the service to check bans.\n",
		# "/setinterval <hours> - Change check interval\n"
		# "/status - Show current check settings\n",
		parse_mode="Markdown"
	)