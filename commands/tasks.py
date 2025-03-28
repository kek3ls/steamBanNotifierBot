import pprint
from telegram import Update
from telegram.ext import CallbackContext
from utils.periodic_checks import active_tasks

async def tasks_command(update: Update, context: CallbackContext):
	userid = update.message.from_user.id

	if userid != 980029762:
		await update.message.reply_text("¡Estas invadiendo!", parse_mode="HTML")
		return

	pretty_tasks = pprint.pformat(active_tasks, indent="\t", width=60)

	formatted_tasks = f"```python\n{pretty_tasks}\n```"

	for char in ["{", "}", "[", "]", "(", ")", ".", "-", "+", "=", "!", "#", "|"]:
		formatted_tasks = formatted_tasks.replace(char, f"\\{char}")

	await update.message.reply_text(formatted_tasks, parse_mode="MarkdownV2")