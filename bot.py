#!/usr/bin/python3
from commands.flush import flush
from commands.start import start
from commands.remove import remove
from commands.cancel import cancel
from commands.add import add_account
from commands.help import help_command
from commands.list import list_accounts
from commands.add import handle_waiting_account
from utils.load_api_keys import TELEGRAM_BOT_KEY
from commands.stop_periodic_checks import stop_ban_check
from commands.start_periodic_checks import start_ban_check
from utils.message_handler import handle_message, handle_unknown_command
from telegram.ext import Application, CommandHandler, filters, MessageHandler

def main():
	app = Application.builder().token(TELEGRAM_BOT_KEY).build()

	# Register command handlers
	app.add_handler(CommandHandler("start", start))

	app.add_handler(CommandHandler("help", help_command))

	app.add_handler(CommandHandler("add", add_account))
	app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_waiting_account))

	app.add_handler(CommandHandler("remove", remove))

	app.add_handler(CommandHandler("list", list_accounts))

	app.add_handler(CommandHandler("flush", flush))

	app.add_handler(CommandHandler("cancel", cancel))
	
	app.add_handler(CommandHandler("startbancheck", start_ban_check))

	app.add_handler(CommandHandler("stopbancheck", stop_ban_check))

	app.add_handler(MessageHandler(filters.COMMAND, handle_unknown_command))
	app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

	print("[INF] Bot is running...")
	app.run_polling()

if __name__ == "__main__":
	main()