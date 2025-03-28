from telegram import Update
from utils.logger import debug_print
from telegram.ext import CallbackContext
from commands.add import accountWaiting as waitingForAccount2Add
from commands.remove import accountWaiting as waitingForAccount2Remove

async def cancel_command(update: Update, context: CallbackContext):
	userid = update.message.from_user.id

	debug_print("debug", f"cancel command requested by {userid}")

	if await waitingForAccount2Remove(userid):
		await waitingForAccount2Remove(userid, False)
		await update.message.reply_text("❌ The action has been cancelled.")
	elif await waitingForAccount2Add(userid):
		await waitingForAccount2Add(userid, False)
		await update.message.reply_text("❌ The action has been cancelled.")
	else:
		await update.message.reply_text("🚫 There is no ongoing action to cancel.")

async def handle_cancel_button(update: Update, context: CallbackContext):
	query = update.callback_query
	userid = query.from_user.id
	await query.answer()

	action = query.data.split("_")[-1]

	if action == "cancel":
		if await waitingForAccount2Remove(userid):
			await waitingForAccount2Remove(userid, False)
			await query.edit_message_text("❌ The action has been cancelled.")
		elif await waitingForAccount2Add(userid):
			await waitingForAccount2Add(userid, False)
			await query.edit_message_text("❌ The action has been cancelled.")
		else:
			await query.edit_message_text("🚫 There is no ongoing action to cancel.")