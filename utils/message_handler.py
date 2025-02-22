from telegram import Update
from telegram.ext import CallbackContext
from utils.telegram_credentials import get as get_credentials
from utils.telegram_credentials import write as write_credentials

VALID_COMMANDS = [
	"/start", "/help", "/add", "/flush", "/remove", "/list",
	"/startbancheck", "/stopbancheck", '/startbc', 'stopbc'
]

async def handle_message(update: Update, context: CallbackContext):
	user_id = update.message.from_user.id  # Get the user's Telegram ID

	print(f"[DBG] list_accounts command received for user_id: {user_id}")

	# Update the user's credentials in the JSON file
	print(f"[DBG] Writing credentials for user_id: {user_id}")
	write_credentials(user_id, get_credentials(update.message.from_user))

	message = update.message

	if message.text:
		print(f"Ordinary message received: {message.text}")
		# await update.message.reply_text("You sent a normal message!")

	# elif message.photo:  # If the message contains a photo
	# 	print("Received a photo")
	# 	await update.message.reply_text("You sent a photo!")

	# elif message.document:  # If the message contains a file/document
	# 	print("Received a document")
	# 	await update.message.reply_text("You sent a document!")

	# elif message.video:  # If the message contains a video
	# 	print("Received a video")
	# 	await update.message.reply_text("You sent a video!")

	# elif message.audio:  # If the message contains an audio file
	# 	print("Received an audio file")
	# 	await update.message.reply_text("You sent an audio file!")

	# elif message.voice:  # If the message contains a voice message
	# 	print("Received a voice message")
	# 	await update.message.reply_text("You sent a voice message!")

	# elif message.sticker:  # If the message contains a sticker
	# 	print("Received a sticker")
	# 	await update.message.reply_text("You sent a sticker!")

	# elif message.location:  # If the message contains a location
	# 	print("Received a location")
	# 	await update.message.reply_text("You sent a location!")

	# elif message.contact:  # If the message contains a contact
	# 	print("Received a contact")
	# 	await update.message.reply_text("You sent a contact!")

	else:
		print("Received an unknown message type")
		# await update.message.reply_text("I don't know what this is!")

async def handle_unknown_command(update: Update, context: CallbackContext):
	user_id = update.message.from_user.id  # Get the user's Telegram ID

	print(f"[DBG] Unknown command received for user_id: {user_id}")

	# Update the user's credentials in the JSON file
	print(f"[DBG] Writing credentials for user_id: {user_id}")
	write_credentials(user_id, get_credentials(update.message.from_user))

	# Extract the unknown command from the message
	command = update.message.text.split()[0]  # Get the first word, which is the command

	print(f"Unknown command received: {command}")
	await update.message.reply_text(
		"⚠️ <b>Unknown command!</b>\n\n"
		"Please use <b>/help</b> to see the list of available commands and get more information. 💡",
		parse_mode="HTML"
	)