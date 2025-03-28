from telegram import Update
from telegram.ext import CallbackContext
from utils.message_handler import handle_message
from commands.remove import process_remove_account
from commands.add import accountWaiting as waitingForAccount2Add
from commands.add import process_account as process_adding_account
from commands.remove import accountWaiting as waitingForAccount2Remove

async def handle_waiting_account(update: Update, context: CallbackContext):
	if await waitingForAccount2Remove(update.message.from_user.id):
		return await process_remove_account(update, context, update.message.text)

	if await waitingForAccount2Add(update.message.from_user.id):
		return await process_adding_account(update, context, update.message.text)

	# If not waiting, treat it as a normal message
	return await handle_message(update, context)

async def isWaitingForInput(update: Update):
	return waitingForAccount2Remove(update.message.from_user.id) or waitingForAccount2Add(update.message.from_user.id)