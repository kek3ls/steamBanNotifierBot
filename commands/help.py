from telegram import Update
from telegram.ext import CallbackContext

async def help_command(update: Update, context: CallbackContext) -> None:
	# Extract user data and update credentials
	user_id = update.message.from_user.id

	print(f"[DBG] help_command received from user_id: {user_id}")

	await update.message.reply_text(
		"📚 <b>Here’s what I can do for you</b>:\n\n"
		"🔹 <b>/start</b> - Start interacting with the bot.\n"
		"🔹 <b>/help</b> - Display this helpful guide.\n"
		"🔹 <b>/add</b> - Add a Steam account to track.\n"
		"🔹 <b>/flush</b> - Check the ban status of your tracked accounts.\n"
		"🔹 <b>/remove</b> - Remove a Steam account from your tracking list.\n"
		"🔹 <b>/list</b> - View all your tracked Steam accounts.\n"
		"🔹 <b>/startbancheck</b> - Start automatic ban checks every 6 hours for your accounts.\n"
		"🔹 <b>/stopbancheck</b> - Stop the automatic ban checks service.\n\n"
		"Need more help or want to contact support? Visit here: <a href='https://k3ls.ru/'>Contacts</a>\n\n"
		"<b><u>Important:</u></b> Before using the bot, please take a moment to read our <a href='https://steambannotifierbot.k3ls.ru/privacyPolicy'>Privacy Policy</a> to understand how we protect and handle your data. 🛡️\n\n"
		# Uncomment below for additional features
		# "<b>/setinterval &lt;hours&gt;</b> - Adjust the interval for checks.\n"
		# "<b>/status</b> - See your current ban check settings.\n",
		,parse_mode="HTML"
	)

	print(f"[INF] Help message sent to user_id: {user_id}")