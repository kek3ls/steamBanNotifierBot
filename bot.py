#!/usr/bin/python3
from commands.flush import flush
from commands.start import start
from commands.remove import remove
from commands.cancel import cancel
from commands.add import add_account
from commands.help import help_command
from commands.list import list_accounts
from utils.load_api_keys import TELEGRAM_BOT_KEY
from commands.stop_periodic_checks import stop_ban_check
from commands.start_periodic_checks import start_ban_check
from utils.telegram_credentials import get as get_credentials
from utils.telegram_credentials import write as write_credentials
from utils.message_handler import handle_message, handle_unknown_command
from commands.add import handle_waiting_account as handle_waiting_account_2_add
from commands.remove import handle_waiting_account as handle_waiting_account_2_remove
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, filters, MessageHandler

async def pre_process(update, context):
	"""Function that runs before any user interaction is handled."""
	
	user_id = update.message.from_user.id

	# Update the user's credentials in the JSON file
	write_credentials(user_id, get_credentials(update.message.from_user))

def main():
	app = Application.builder().token(TELEGRAM_BOT_KEY).build()

	# Execute writing credentials before everything else
	app.add_handler(MessageHandler(filters.ALL & ~filters.Command("start") & ~filters.Command("help"), pre_process), group=-1)

	# Register command handlers
	app.add_handler(CommandHandler("start", start))
	app.add_handler(CommandHandler("help", help_command))
	app.add_handler(CommandHandler("list", list_accounts))
	app.add_handler(CommandHandler("flush", flush))
	app.add_handler(CommandHandler("startbancheck", start_ban_check))
	app.add_handler(CommandHandler("stopbancheck", stop_ban_check))

	app.add_handler(CommandHandler("add", add_account))
	app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_waiting_account_2_add))
	app.add_handler(CommandHandler("remove", remove))
	app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_waiting_account_2_remove))
	app.add_handler(CallbackQueryHandler(cancel))

	# Handle unknown commands and plain text messages
	app.add_handler(MessageHandler(filters.COMMAND, handle_unknown_command))
	app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

	print("[INF] Bot is running...")
	app.run_polling()

if __name__ == "__main__":
	main()