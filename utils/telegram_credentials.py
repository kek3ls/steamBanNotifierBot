from telegram import Update
from datetime import datetime
from utils.logger import debug_print
from utils.date import convert as to_iso
from utils.data_editor import save_data, load_data, validate

# Function to extract and format Telegram user data
def get_userdata(update: Update):
	user = update.message.from_user

	timeStamp = to_iso(datetime.now().isoformat(), True)

	user_info = {
		"username": user.username,
		"id": user.id,
		"name": {
			"name": user.first_name or None,
			"surname": user.last_name or None
		},
		"isBot": user.is_bot or False,
		"isPremium": user.is_premium or False,
		"languageCode": user.language_code or None,
		"latestUpdate": timeStamp or None
	}

	return user_info

async def write(update: Update):
	userid = update.message.from_user.id

	await validate(userid)

	debug_print("info", f"writing credentials for {userid}")

	data = await load_data(userid)

	user_data = get_userdata(update)

	# debug_print("info", user_data)

	data["credentials"] = user_data

	# Save the updated data back to the JSON file
	await save_data(userid, data)
	debug_print("info", f"credentials updated for {userid}")