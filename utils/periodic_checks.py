import os
import json
import asyncio
from telegram import Bot
from utils.logger import debug_print
from utils.data_editor import load_data, save_data
from utils.steam_api import check_ban_status, get_nickname

# Path to save active users' states
TASKS_FILE = "active_tasks.json"
active_tasks = {}

# Load active tasks from file on bot startup
def load_active_tasks():
	if os.path.exists(TASKS_FILE):
		try:
			with open(TASKS_FILE, "r") as f:
				data = json.load(f)

				if isinstance(data, dict):
					return data.get("active_users", [])
				else:
					debug_print('error', "Invalid format in active_tasks.json. Resetting file.")
		except json.JSONDecodeError:
			debug_print('error', "active_tasks.json is corrupted. Resetting file.")

	return []  # Return an empty list if the file is missing or corrupted

# Save active tasks to file
def save_active_tasks():
	with open(TASKS_FILE, "w") as f:
		json.dump({"active_users": list(active_tasks.keys())}, f, indent="\t")

async def periodic_ban_check(bot: Bot, userid: int):
	while True:
		try:
			if not await stateEditor(userid):  
				debug_print('info', f"Ban checking stopped for {userid}")
				break  # Exit loop if user disabled ban tracking

			if not os.path.exists("userdata"):
				debug_print('debug', "Creating 'userdata' directory.")
				os.makedirs("userdata")

			for filename in os.listdir("userdata"):
				if filename.endswith(".json"):
					current_userid = int(filename.split(".json")[0])  
					debug_print('debug', f"Processing user data for {current_userid}")
					data = await load_data(current_userid)

					for account in data["trackedAccounts"]:
						steamid64 = account["steamid"]
						previous_ban_state = account.get("ban", {})
						# debug_print("info", "prev. ban state " + str(previous_ban_state))

						ban_state_table = await check_ban_status(userid, steamid64, True)

						# debug_print("info", "curr. ban state " + str(ban_state_table))
						
						# Ensure the returned value is a dictionary
						if not isinstance(ban_state_table, dict):
							debug_print('error', f"Invalid ban state for {steamid64}: {ban_state_table} (expected dict)")
							continue  # Skip to next account if something went wrong

						# debug_print("info", str(ban_state_table == previous_ban_state) + f" for {steamid64}")

						# If ban state has changed (compare dictionaries)
						if ban_state_table != previous_ban_state:
							debug_print('info', f"Ban state changed for {steamid64}: {ban_state_table}")
							
							# Format the table (dictionary) into a human-readable string
							ban_state_string = check_ban_status(userid, steamid64, False)
							
							# Send formatted message to the user
							display_name = await get_nickname(steamid64, userid)
							steam_profile_url = f"https://steamcommunity.com/profiles/{steamid64}"

							message = f"🚨 <a href='{steam_profile_url}'>{display_name}</a> has been banned: {ban_state_string}"

							debug_print('info', f"Sending ban notification to {current_userid}")
							await bot.send_message(chat_id=current_userid, text=message, parse_mode="HTML")

							# Update the 'ban' field with the new ban status
							account["ban"] = ban_state_table
							await save_data(current_userid, data)
							debug_print('info', f"Ban notification sent and status updated for {steamid64}.")

			try:
				interval_hours = await interval(userid)
			except Exception as e:
				debug_print('error', f"Failed to fetch interval for {userid}: {e}")
				interval_hours = 6  # Default to 6 hours if an error occurs

			debug_print('debug', f"Sleeping for {interval_hours} hours before next check.")
			await asyncio.sleep(interval_hours * 3600)

		except asyncio.CancelledError:
			debug_print('info', f"Ban check task for {userid} was cancelled.")
			break  
		except Exception as e:
			debug_print('error', f"Unexpected error in periodic_ban_check for {userid}: {e}")
			await asyncio.sleep(6 * 3600)  # Delay before retrying

async def resume_tasks(app):
	"""Resumes periodic checks for users who had active tasks before bot shutdown."""
	stored_tasks = load_active_tasks()
	debug_print('info', f"Resuming {len(stored_tasks)} periodic ban checks from previous session.")

	for userid in stored_tasks:
		if userid not in active_tasks and await stateEditor(userid):
			debug_print('info', f"Starting periodic ban check for {userid}")
			active_tasks[userid] = asyncio.create_task(periodic_ban_check(app.bot, int(userid)))

	debug_print("info", f"Active tasks after resuming: {active_tasks}")

async def stateEditor(userid, state: bool = None):
	"""Edits or retrieves the state of periodic checks for a user."""
	data = await load_data(userid)

	if state is None:
		return data["globals"].get("periodicCheck", False)
	else:
		data["globals"]["periodicCheck"] = state
		await save_data(userid, data)

async def interval(userid, hours: int = None):
	"""Gets or sets the interval for ban checks."""
	data = await load_data(userid)

	if hours is None:
		return data["globals"].get("intervalHours", 6)  # Default to 6 hours
	else:
		data["globals"]["intervalHours"] = int(hours)
		await save_data(userid, data)