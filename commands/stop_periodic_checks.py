from telegram import Update
from telegram.ext import CallbackContext
from commands.start_periodic_checks import running_tasks  # Global tracking

async def stop_ban_check(update: Update, context: CallbackContext):
	user_id = update.message.chat_id  # Unique identifier for the user

	# Check if the user has an active periodic check running
	if user_id in running_tasks:
		del running_tasks[user_id]  # Stop tracking the user's task
		await update.message.reply_text("❌ You will no longer receive ban notifications.")

		# If no users are left with active checks, stop the global task
		if not running_tasks:  # No more users with active checks
			if "global" in running_tasks:
				running_tasks["global"].cancel()  # Stop the global task
				del running_tasks["global"]
				await update.message.reply_text("🛑 All periodic ban checks have been stopped.")
	else:
		await update.message.reply_text("⚠️ No active ban checks are running for your accounts.")