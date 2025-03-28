from os import remove as os_remove
from utils.logger import debug_print
from utils.buttons import new_button
from telegram.ext import CallbackContext
from utils.data_editor import get_user_file
from telegram import InlineKeyboardMarkup, Update, InputMediaDocument

async def handle_data_buttons(update: Update, context: CallbackContext):
	query = update.callback_query
	await query.answer()

	action = query.data.split("_")[-1]

	if action == "delete":
		await query.edit_message_text("🔄 Processing, please wait...")
		try:
			os_remove(get_user_file(query.from_user.id))
			await query.edit_message_text("✅ File has been deleted.")
		except FileNotFoundError:
			await query.edit_message_text("⚠️ Oops, it appears that we dont have your data. :P")
		except Exception as e:
			await query.edit_message_text(f"❌ Error deleting file: {str(e)}")

	elif action == "send":
		await query.edit_message_text("🔄 Processing, please wait...")
		try:
			with open(get_user_file(query.from_user.id), "rb") as file:
				await query.edit_message_media(InputMediaDocument(file))
		except FileNotFoundError:
			await query.edit_message_text("⚠️ Oops, it appears that we dont have your data. :P")
		except Exception as e:
			await query.edit_message_text(f"❌ Error sending file: {str(e)}")

async def data_command(update: Update, context: CallbackContext):
	userid = update.message.from_user.id

	debug_print("debug", f"cancel command requested by {userid}")

	buttons = [
		[new_button("🔍 Review", handle_data_buttons, "send"),
		new_button("🗑️ Delete", handle_data_buttons, "delete")]
	]

	await update.message.reply_text(
		"📌 Please choose an option below:\n\n"
		"\"<b>🔍 Review</b>\" - send your data file.\n"
		"\"<b>🗑️ Delete</b>\" - remove the data file from our servers. Be warned, the data deletion is irreversible! <b>You will lose every account</b> stored in the bot.",
		parse_mode="HTML",
		reply_markup=InlineKeyboardMarkup(buttons)
	)