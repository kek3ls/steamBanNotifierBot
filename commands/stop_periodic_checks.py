from telegram import Update
from telegram.ext import CallbackContext
from commands.start_periodic_checks import running_tasks
from utils.telegram_credentials import get as get_credentials
from utils.telegram_credentials import write as write_credentials

async def stop_ban_check(update: Update, context: CallbackContext):
	user_id = update.message.chat_id  # Unique identifier for the user

	print(f"[DBG] Received stop ban check request for user_id: {user_id}")

	# Update the user's credentials in the JSON file
	print(f"[DBG] Writing credentials for user_id: {user_id}")
	write_credentials(user_id, get_credentials(update.message.from_user))

	# Check if the user has an active periodic check running
	if user_id in running_tasks:
		print(f"[INF] Found active ban check for user_id: {user_id}. Stopping task.")
		del running_tasks[user_id]  # Stop tracking the user's task
		await update.message.reply_text("❌ <b>Ban check notifications have been stopped</b> for your tracked accounts.", parse_mode="HTML")

		# If no users are left with active checks, stop the global task
		if not running_tasks:  # No more users with active checks
			if "global" in running_tasks:
				print("[INF] No more active user tasks. Stopping global task.")
				running_tasks["global"].cancel()  # Stop the global task
				del running_tasks["global"]
				await update.message.reply_text("🛑 <b>All periodic ban checks have been stopped</b>.", parse_mode="HTML")
	else:
		print(f"[WRN] No active ban check found for user_id: {user_id}")
		await update.message.reply_text("⚠️ <b>No active ban checks are running</b> for your accounts.", parse_mode="HTML")