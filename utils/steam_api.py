import httpx
from utils.load_api_keys import STEAM_API_KEY

# Async function to get the player's nickname
async def get_player_nickname(steamid64):
	url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={STEAM_API_KEY}&steamids={steamid64}"

	try:
		async with httpx.AsyncClient() as client:
			response = await client.get(url)
			if response.status_code == 200:
				data = response.json()
				if "response" in data and "players" in data["response"]:
					players = data["response"]["players"]
					if players:
						return players[0].get("personaname", None)
	except Exception as e:
		print(f"Error fetching nickname for SteamID64 {steamid64}: {e}")
	return None

async def check_ban_status(steamid64):
	url = f"https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={STEAM_API_KEY}&steamids={steamid64}"

	try:
		async with httpx.AsyncClient() as client:
			response = await client.get(url)
			if response.status_code == 200:
				data = response.json()
				if "players" in data and len(data["players"]) > 0:
					player_data = data["players"][0]

					# Extract ban details
					vac_banned = player_data.get("VACBanned", False)
					community_banned = player_data.get("CommunityBanned", False)
					economy_ban = player_data.get("EconomyBan", "none")
					limited_account = player_data.get("LimitedAccount", False)
					number_of_game_bans = player_data.get("NumberOfGameBans", 0)

					# Create ban message
					ban_state = []
					if vac_banned:
						ban_state.append("✅ VAC")
					if community_banned:
						ban_state.append("✅ Community")
					if economy_ban != "none":
						ban_state.append(f"💵 Economy Ban: {economy_ban}")
					if limited_account:
						ban_state.append("🔞 Limited Account")
					if number_of_game_bans > 0:
						ban_state.append(f"✅ Game Bans: {number_of_game_bans}")

					return ", ".join(ban_state) if ban_state else None

	except Exception as e:
		return f"Error checking ban state for SteamID64 {steamid64}: {e}"