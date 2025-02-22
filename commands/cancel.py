from telegram import Update
from telegram.ext import CallbackContext
from utils.constants import WAITING_FOR_ACCOUNT

async def cancel(update: Update, context: CallbackContext):
    """Handles the /cancel command to abort the process."""
    if context.user_data.get(WAITING_FOR_ACCOUNT):
        await update.message.reply_text("🛑 The action has been cancelled.")
        context.user_data.pop(WAITING_FOR_ACCOUNT, None)
    else:
        await update.message.reply_text("❌ There is no ongoing action to cancel.")