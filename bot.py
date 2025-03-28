#!/usr/bin/python3
from utils.load_api_keys import TELEGRAM_BOT_KEY  # Import bot api key before everything as dummy-check

from telegram import Update
from commands.add import add_command
from utils.logger import debug_print
from utils.data_editor import validate
from commands.help import help_command
from commands.list import list_command
from commands.start import start_command
from commands.flush import flush_command
from commands.remove import remove_command
from utils.periodic_checks import resume_tasks
from commands.set_interval import interval_command
from utils.account_waiting import handle_waiting_account
from commands.data import data_command, handle_data_buttons
from commands.stop_periodic_checks import stopbancheck_command
from commands.cancel import cancel_command, handle_cancel_button
from commands.start_periodic_checks import startbancheck_command
from utils.telegram_credentials import write as write_credentials
from utils.message_handler import handle_message, handle_unknown_command
from telegram.ext import Application, CommandHandler, filters, MessageHandler, CallbackContext, CallbackQueryHandler
# from commands.tasks import send_active_tasks

async def on_startup(app: Application):
	await resume_tasks(app)

user_interactions = {}

async def pre_process(update: Update, context: CallbackContext):
	from commands.add import accountWaiting as waitingForAccount2Add
	from commands.remove import accountWaiting as waitingForAccount2Remove

	message = update.message.text

	ignored_commands = {"/start", "/help"}

	if message in ignored_commands:
		return

	userid = update.message.from_user.id

	# Disable any account waitings upon first interaction. Dummy-check
	if userid not in user_interactions:
		await waitingForAccount2Add(userid, False)
		await waitingForAccount2Remove(userid, False)
		user_interactions[userid] = True

	await validate(update.message.from_user.id)
	await write_credentials(update)

def main():
	app = Application.builder().token(TELEGRAM_BOT_KEY).post_init(on_startup).build()

	app.add_handler(MessageHandler(filters.ALL, pre_process), group=0)

	# Register command handlers
	app.add_handler(CommandHandler("start", start_command), group=2)
	app.add_handler(CommandHandler("help", help_command), group=2)
	app.add_handler(CommandHandler("add", add_command), group=2)
	app.add_handler(CommandHandler("remove", remove_command), group=2)
	app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_waiting_account), group=2)
	app.add_handler(CommandHandler("list", list_command), group=2)
	app.add_handler(CommandHandler("flush", flush_command), group=2)
	app.add_handler(CommandHandler("cancel", cancel_command), group=2)
	app.add_handler(CommandHandler("startbancheck", startbancheck_command), group=2)
	app.add_handler(CommandHandler("startbc", startbancheck_command), group=2)
	app.add_handler(CommandHandler("stopbancheck", stopbancheck_command), group=2)
	app.add_handler(CommandHandler("stopbc", stopbancheck_command), group=2)
	app.add_handler(CommandHandler("data", data_command), group=2)
	app.add_handler(CommandHandler("interval", interval_command), group=2)
	# app.add_handler(CommandHandler("tasks", send_active_tasks), group=2)
	app.add_handler(CallbackQueryHandler(handle_cancel_button), group=2)
	app.add_handler(CallbackQueryHandler(handle_data_buttons), group=3)

	# Handle unknown commands and plain text messages
	app.add_handler(MessageHandler(filters.COMMAND, handle_unknown_command))
	app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

	debug_print("info", "Bot is running...")
	app.run_polling()

if __name__ == "__main__":
	main()