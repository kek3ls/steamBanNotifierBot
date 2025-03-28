import asyncio
from telegram import Update
from utils.logger import debug_print
from telegram.ext import CallbackContext
from utils.periodic_checks import stateEditor, active_tasks, save_active_tasks

async def stopbancheck_command(update: Update, context: CallbackContext):
	"""Stops the periodic ban check for the user."""
	userid = update.message.chat_id
	debug_print("debug", f"stop_ban_check command requested by {userid}")

	# debug_print('debug', f"Active tasks before stopping: {active_tasks}")

	if userid in active_tasks:
		task = active_tasks[userid]
		debug_print('debug', f"Task found for {userid}, done status: {task.done()}")

		if not task.done():
			debug_print('info', f"Stopping periodic ban check for {userid}")
			task.cancel()  # Cancel the task
			try:
				await task  # Ensure the task is properly cancelled
			except asyncio.CancelledError:
				debug_print('info', f"Periodic ban check task for {userid} was canceled.")

			# Remove the task from the active_tasks dictionary and save state
			del active_tasks[userid]
			save_active_tasks()

			await stateEditor(userid, False)  # Mark the state as False, meaning no active task.

			# Inform the user
			await update.message.reply_text("❌ <b>Ban check notifications have been stopped</b> for your tracked accounts.", parse_mode="HTML")
		else:
			debug_print('warning', f"Task for {userid} was already completed.")
			await update.message.reply_text("⚠️ <b>No active ban checks are running</b> for your accounts.", parse_mode="HTML")
	else:
		debug_print('warning', f"No active ban check found for {userid}")
		await update.message.reply_text("⚠️ <b>No active ban checks are running</b> for your accounts.", parse_mode="HTML")