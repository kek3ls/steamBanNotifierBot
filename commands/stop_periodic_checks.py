from telegram import Update
from telegram.ext import CallbackContext
from commands.start_periodic_checks import running_tasks  # Global tracking

async def stop_ban_check(update: Update, context: CallbackContext):
    user_id = update.message.chat_id  # Unique per user

    # Check if the user has an active periodic check running
    if user_id in running_tasks:
        del running_tasks[user_id]  # Remove the user from tracking
        await update.message.reply_text("❌ You will no longer receive periodic ban check updates.")

        # If no users are left in tracking, stop the global task
        if not running_tasks:  # If there are no more users with active checks
            if "global" in running_tasks:
                running_tasks["global"].cancel()  # Stop the global task
                del running_tasks["global"]
                await update.message.reply_text("🛑 All periodic ban checks have been stopped.")
    else:
        await update.message.reply_text("⚠️ No active ban checks are running for your account.")
