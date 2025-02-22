import asyncio
from telegram import Update
from telegram.ext import CallbackContext
from utils.telegram_credentials import get as get_credentials
from utils.periodic_checks import periodic_ban_check, load_data
from utils.telegram_credentials import write as write_credentials

# Dictionary to keep track of running tasks per user
running_tasks = {}

async def start_ban_check(update: Update, context: CallbackContext):
	user_id = update.message.chat_id  # Unique identifier for the user

	print(f"[DBG] start_ban_check command received for user_id: {user_id}")

	# Update the user's credentials in the JSON file
	print(f"[DBG] Writing credentials for user_id: {user_id}")
	write_credentials(user_id, get_credentials(update.message.from_user))

	data = load_data(user_id)  # Load user-specific tracking data
	interval_hours = data.get("interval_hours", 6)

	# Check if a task is already running for this user
	if user_id in running_tasks:
		print(f"[WRN] A ban check is already running for user_id: {user_id}")
		await update.message.reply_text("⚠️ A ban check is already running for your tracked accounts. Please wait for the current check to finish.")
		return

	# Start a periodic ban check task for this user
	print(f"[DBG] Starting periodic ban check for user_id: {user_id}")
	task = asyncio.create_task(periodic_ban_check(context.bot, user_id))  # Pass user_id if needed
	running_tasks[user_id] = task  # Track the user's task

	await update.message.reply_text(
		f"✅ <b>Periodic ban checks</b> have been successfully started!\n\n"
		f"Your tracked accounts will be checked every <b>{interval_hours} hours</b>.\n\n"
		"Stay tuned for updates on their ban status. 🕒",
		parse_mode="HTML"
	)

	print(f"[INF] Periodic ban check started for user_id: {user_id} every {interval_hours} hours.")