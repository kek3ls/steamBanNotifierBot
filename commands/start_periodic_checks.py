import asyncio
from telegram import Update
from utils.logger import debug_print
from telegram.ext import CallbackContext
from utils.periodic_checks import periodic_ban_check, stateEditor, interval, active_tasks, save_active_tasks

async def startbancheck_command(update: Update, context: CallbackContext):
	userid = update.message.chat_id

	debug_print('debug', f"start_ban_check command requested by {userid}")

	interval_hours = await interval(userid)

	# Check if a task is already running for this user
	if userid in active_tasks:
		task = active_tasks[userid]
		if not task.done():  # Only check if the task is not finished or canceled
			debug_print('warning', f"A ban check is already running for {userid}")
			await update.message.reply_text("⚠️ A ban check is already running for your tracked accounts.")
			return
		else:
			# If the task is done, we remove it from active tasks
			# Whether the task finished successfully or with an error, we should remove it
			debug_print('info', f"Task for {userid} already completed with status: {task.done()} - removing task and restarting.")
			del active_tasks[userid]  # Remove the completed task

	# Start a periodic ban check task for this user
	debug_print('debug', f"Starting periodic ban check for {userid}")
	await stateEditor(userid, True)  # Mark the task as running

	# Start the periodic task in the background using asyncio.create_task()
	active_tasks[userid] = asyncio.create_task(periodic_ban_check(context.bot, userid))  # This runs in the background
	save_active_tasks()  # Save active tasks after starting a new one

	await update.message.reply_text(
		f"✅ <b>Periodic ban checks</b> have been successfully started!\n\n"
		f"Your tracked accounts will be checked every <b>{interval_hours} hours</b>.\n\n"
		"Stay tuned for updates on their ban status. 🕒",
		parse_mode="HTML"
	)

	debug_print('info', f"Periodic ban check started for {userid} every {interval_hours} hours.")