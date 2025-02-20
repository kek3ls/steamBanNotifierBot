from telegram import Update
from telegram.ext import CallbackContext
from utils.save_credentials import update_user_credentials, extract_telegram_user_data

async def start(update: Update, context: CallbackContext) -> None:
	# Extract user data and update credentials
	user_id = update.message.from_user.id
	telegram_user_data = extract_telegram_user_data(update.message.from_user)
	
	# Update the user's credentials in the JSON file
	update_user_credentials(user_id, telegram_user_data)
	
	await update.message.reply_text(
		"✅ Greetings!\n\n"
		"Type /help to view the list of available commands."
	)