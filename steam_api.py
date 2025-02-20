import httpx
import logging
from utils.load_api_keys import STEAM_API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO)

# Function to get Steam bans using the Steam ID
async def get_ban_info(steam_id: str):
	url = f'https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/'
	params = {
		'key': STEAM_API_KEY,
		'steamids': steam_id
	}
	
	try:
		async with httpx.AsyncClient() as client:
			logging.info(f"Requesting ban info for SteamID: {steam_id}")
			response = await client.get(url, params=params)
			data = response.json()

			if 'players' in data:
				player_data = data['players'][0]
				if player_data:
					return player_data
				else:
					logging.warning(f"No player data found for SteamID: {steam_id}")
			else:
				logging.error(f"Error fetching data for SteamID: {steam_id}")
				
	except httpx.RequestError as e:
		logging.error(f"Request failed: {e}")
	return None

# Function to extract ban status and details
def check_ban_status(ban_info):
	if not ban_info:
		return "Could not retrieve ban information."
	
	vac_banned = ban_info.get('VACBanned', False)
	game_banned = ban_info.get('NumberOfGameBans', 0)
	community_banned = ban_info.get('CommunityBanned', False)

	ban_message = []
	
	if vac_banned:
		ban_message.append("VAC Banned")
	if game_banned > 0:
		ban_message.append(f"Game Banned (Games: {game_banned})")
	if community_banned:
		ban_message.append("Community Banned")

	if not ban_message:
		return "No bans found."

	return ", ".join(ban_message)