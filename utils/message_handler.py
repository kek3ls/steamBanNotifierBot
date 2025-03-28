from telegram import Update
from utils.logger import debug_print
from telegram.ext import CallbackContext

async def handle_message(update: Update, context: CallbackContext):
	userid = update.message.from_user.id

	message = update.message.text

	if message:
		debug_print('debug', f"Received an ordinary message from {userid}: {message}")
		await update.message.reply_text("Say waaaat???")

	else:
		debug_print('warning', f"Received an unknown message type from {userid}")
		# await update.message.reply_text("I don't know what this is!")

async def handle_unknown_command(update: Update, context: CallbackContext):
	userid = update.message.from_user.id

	# Extract the unknown command from the message
	command = update.message.text.split()[0]  # Get the first word, which is the command

	debug_print('warning', f"Unknown command received from {userid}: {command}")
	await update.message.reply_text(
		"⚠️ <b>Unknown command</b>!\n\n"
		"Please use /<b>help</b> to see the list of available commands and get more information. 💡",
		parse_mode="HTML"
	)