import asyncio
from telegram import Update
from telegram.ext import CallbackContext
from utils.periodic_checks import periodic_ban_check, load_data

# Dictionary to keep track of running tasks per user
running_tasks = {}

async def start_ban_check(update: Update, context: CallbackContext):
	user_id = update.message.chat_id  # Unique identifier for the user
	data = load_data(user_id)  # Load user-specific tracking data
	interval_hours = data.get("interval_hours", 6)

	# Check if a task is already running for this user
	if user_id in running_tasks:
		await update.message.reply_text("⚠️ A ban check is already running for your tracked accounts.")
		return

	# Start a periodic ban check task for this user
	task = asyncio.create_task(periodic_ban_check(context.bot, user_id))  # Pass user_id if needed
	running_tasks[user_id] = task  # Track the user's task

	await update.message.reply_text(
		f"✅ Periodic ban checks have been started. "
		f"Checks will run every {interval_hours} hours for your tracked accounts."
	)