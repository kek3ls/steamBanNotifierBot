from telegram import Update
from utils.logger import debug_print
from telegram.ext import CallbackContext

async def start_command(update: Update, context: CallbackContext) -> None:
	userid = update.message.from_user.id

	debug_print("debug", f"start command requested by {userid}")

	await update.message.reply_text(
		"👋 <b>Greetings</b> and <b>welcome</b>! 🎉\n\n" \
		"Before diving in, we highly recommend reviewing our " \
		"<a href='https://steambannotifierbot.k3ls.ru/privacyPolicy'><b>Privacy Policy</b></a>, " \
		"to fully understand how <b>we collect</b> and handle <b>your data</b>. 🔒\n\n" \
		"Rest assured, the /<b>start</b> and /<b>help</b> commands does <b>not</b> collect <b>any personal data</b>.\n" \
		"You can use them freely to explore the available features! 📝🚀\n\n" \
		"Once you're ready, type /<b>help</b> to get started and see the list of commands."
		,parse_mode="HTML" # keep the comma before "parse_mode" in case of adding any more lines
	)

	debug_print("info", f"start sent to {userid}")