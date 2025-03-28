from telegram import InlineKeyboardButton

def new_button(name: str, callback_function, *args) -> InlineKeyboardButton:
	callback_data = f"{callback_function.__name__}_{args[0]}"
	
	return InlineKeyboardButton(name, callback_data=callback_data)