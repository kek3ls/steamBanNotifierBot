from dotenv import load_dotenv
from os import getenv as get_env_var
from utils.logger import debug_print

load_dotenv()

class MissingAPIKey(Exception):
	pass

def get_api_key(env_var):
	key = get_env_var(env_var, None)

	if not key:
		raise MissingAPIKey(f"{env_var} API key is missing or invalid.")

	return key

TELEGRAM_BOT_KEY = get_api_key("Telegram")
STEAM_API_KEY = get_api_key("Steam")

debug_print("info", "API keys are valid, continuing the execution...")