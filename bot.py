#!/usr/bin/python3
import json
from telegram.ext import Application, CommandHandler
from commands.start import start
from commands.help import help_command
from commands.add import add_account
from commands.remove import remove
from commands.list import list_accounts
from commands.flush import flush
from commands.start_periodic_checks import start_ban_check
from commands.stop_periodic_checks import stop_ban_check
from utils.load_api_keys import TELEGRAM_BOT_KEY

def main():
	app = Application.builder().token(TELEGRAM_BOT_KEY).build()

	# Register command handlers
	app.add_handler(CommandHandler("start", start))
	app.add_handler(CommandHandler("help", help_command))
	app.add_handler(CommandHandler("add", add_account))
	app.add_handler(CommandHandler("remove", remove))
	app.add_handler(CommandHandler("list", list_accounts))
	app.add_handler(CommandHandler("flush", flush))
	app.add_handler(CommandHandler("startbancheck", start_ban_check))
	app.add_handler(CommandHandler("stopbancheck", stop_ban_check))

	print("Bot is running...")
	app.run_polling()

if __name__ == "__main__":
	main()