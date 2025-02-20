import json

def load_api_keys():
	with open("utils/api_keys.json", "r") as file:
		data = json.load(file)

	telegram_key = data.get("TelegramBotApiKey", [{}])[0].get("value", "")
	steam_key = data.get("SteamAPIKey", [{}])[0].get("value", "")

	return telegram_key, steam_key

# Load both keys
TELEGRAM_BOT_KEY, STEAM_API_KEY = load_api_keys()