from telegram import Update
from telegram.ext import CallbackContext

async def start(update: Update, context: CallbackContext) -> None:
	user_id = update.message.from_user.id

	print(f"[DBG] start command received from user_id: {user_id}")

	await update.message.reply_text(
		"👋 <b>Greetings</b>!\n\n"
		"Welcome to the bot! 🤖\n\n"
		"Before you get started, we strongly encourage you to review our <b>Privacy Policy</b> to understand how we handle your data. You can find it here: "
		"<a href='https://steambannotifierbot.k3ls.ru/privacyPolicy'>Privacy Policy</a>. 🛡️\n\n"
		"To get started, type /help and explore the list of available commands. 📝",
		parse_mode="HTML"
	)

	print(f"[INF] Greeting sent to user_id: {user_id}")