from telegram import Update
from utils.logger import debug_print
from telegram.ext import CallbackContext
from utils.periodic_checks import interval

async def interval_command(update: Update, context: CallbackContext) -> None:
	userid = update.message.from_user.id

	debug_print("debug", f"interval command requested by {userid}")

	if not context.args:
		await update.message.reply_text("Please provide the value as a number 1-24.", parse_mode="HTML")
		return

	message = context.args[0]

	try:
		interval_value = float(message)
	except ValueError:
		await update.message.reply_text("The argument is <b>not a number</b>, please try again.", parse_mode="HTML")
		return

	if interval_value > 24:
		await update.message.reply_text("Given number is <b>greater than 24</b>, please try again.", parse_mode="HTML")
		return
	elif interval_value < 1:
		await update.message.reply_text("Given number is <b>lower than 1</b>, please try again.", parse_mode="HTML")
		return

	interval_value = max(1, min(interval_value, 24))  # Just in case :P

	# Set the interval
	await interval(userid, interval_value)

	# Verify the change by retrieving the current interval
	current_interval = await interval(userid)

	if current_interval == interval_value:
		await update.message.reply_text("Successfully changed interval.", parse_mode="HTML")
	else:
		await update.message.reply_text("There was some error, please try again later or contact <a href='https://k3ls.ru/'>support</a>.", parse_mode="HTML")
