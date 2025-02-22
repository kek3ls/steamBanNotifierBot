from telegram import Update
from telegram.ext import CallbackContext
from utils.telegram_credentials import get as get_credentials
from utils.telegram_credentials import write as write_credentials

async def start(update: Update, context: CallbackContext) -> None:
	user_id = update.message.from_user.id

	print(f"[DBG] start command received from user_id: {user_id}")

	# Update the user's credentials in the JSON file
	print(f"[DBG] Writing credentials for user_id: {user_id}")
	write_credentials(user_id, get_credentials(update.message.from_user))

	await update.message.reply_text(
		"👋 <b>Greetings</b>!\n\n"
		"Welcome to the bot! 🤖\n\n"
		"To get started, type /help and explore the list of available commands. 📝",
		parse_mode="HTML"
	)

	print(f"[INF] Greeting sent to user_id: {user_id}")