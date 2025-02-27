from telegram import Update
from telegram.ext import CallbackContext

async def cancel(update: Update, context: CallbackContext):
	"""Handles the /cancel command and inline cancel button."""
	query = update.callback_query
	await query.answer()  # Acknowledge the callback to stop flashing

	user_id = query.from_user.id
	context.user_data.pop("WAITING_FOR_ACCOUNT_2_ADD", None)
	context.user_data.pop("WAITING_FOR_ACCOUNT_2_REMOVE", None)

	# Edit the original message to confirm cancellation
	await query.message.edit_text("❌ Action canceled.")