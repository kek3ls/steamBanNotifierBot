import re
import httpx
import requests
from utils.load_api_keys import STEAM_API_KEY
from utils.data_editor import save_data, load_data

async def to_steamid64(input: str):
	input = input.strip()
	print(f"[DBG] Received input: {input}")

	if input.startswith("https://s.team/p/"):
		print(f"[DBG] Detected Steam short link: {input}")
		resolved_url = await resolve_steam_shortlink(input)
		if resolved_url:
			print(f"[INF] Resolved short link to: {resolved_url}")
			input = resolved_url

	profile_url_pattern = r"^https?://steamcommunity\.com/profiles/(\d+)/?$"
	profile_url_match = re.match(profile_url_pattern, input)
	if profile_url_match:
		print(f"[INF] Matched profile URL with SteamID64: {profile_url_match.group(1)}")
		return profile_url_match.group(1)

	custom_url_pattern = r"^https?://steamcommunity\.com/id/([a-zA-Z0-9_]+)/*$"
	print(f"[DBG] Checking custom URL pattern for: {input}")
	custom_url_match = re.match(custom_url_pattern, input)
	if custom_url_match:
		print(f"[INF] Matched custom URL: {custom_url_match.group(1)}")
		return await resolve_steamid_from_custom_url(custom_url_match.group(1))
	else:
		print(f"[WRN] Custom URL match failed for: {input}")

	if input.isdigit() and len(input) == 17:
		print(f"[INF] Detected SteamID64 directly: {input}")
		return input

	steamid3_pattern = r"\[U:1:(\d+)\]"
	steamid3_match = re.match(steamid3_pattern, input)
	if steamid3_match:
		print(f"[INF] Matched SteamID3 format: {steamid3_match.group(1)}")
		return steamid3_to_steamid64(steamid3_match.group(1))

	print(f"[ERR] No match found for input: {input}")
	return None

async def resolve_steam_shortlink(short_url):
	try:
		print(f"[DBG] Resolving short link: {short_url}")
		response = requests.get(short_url, allow_redirects=True)
		if response.status_code == 200:
			final_url = response.url
			print(f"[INF] Resolved short link to: {final_url}")
			return final_url
		else:
			print(f"[ERR] Failed to resolve short link: {response.status_code}")
			return None
	except requests.exceptions.RequestException as e:
		print(f"[ERR] Error resolving short link: {e}")
		return None

async def resolve_steamid_from_custom_url(custom_url):
	print(f"[DBG] Resolving SteamID64 from custom URL: {custom_url}")
	url = f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?key={STEAM_API_KEY}&vanityurl={custom_url}"
	try:
		response = requests.get(url)
		if response.status_code == 200:
			data = response.json()
			if data.get("response", {}).get("steamid"):
				print(f"[INF] Resolved SteamID64 from custom URL: {data['response']['steamid']}")
				return data["response"]["steamid"]
			else:
				print(f"[WRN] Failed to resolve custom URL: {custom_url}")
				return None
		else:
			print(f"[ERR] API response error: {response.status_code}, {response.text}")
			return None
	except requests.exceptions.RequestException as e:
		print(f"[ERR] Error resolving custom URL: {e}")
		return None

def steamid3_to_steamid64(steamid3):
	steamid64 = str(int(steamid3) + 76561197960265728)
	print(f"[INF] Converted SteamID3 to SteamID64: {steamid64}")
	return steamid64

async def get_player_nickname(steamid64):
	print(f"[DBG] Fetching nickname for SteamID64: {steamid64}")
	url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={STEAM_API_KEY}&steamids={steamid64}"
	try:
		async with httpx.AsyncClient() as client:
			response = await client.get(url)
			if response.status_code == 200:
				data = response.json()
				if "response" in data and "players" in data["response"]:
					players = data["response"]["players"]
					if players:
						print(f"[INF] Fetched nickname: {players[0].get('personaname', None)}")
						return players[0].get("personaname", None)
	except Exception as e:
		print(f"[ERR] Error fetching nickname for SteamID64 {steamid64}: {e}")
	return None

async def update_ban_status(user_id, steamid64):
	# Step 1: Get the ban status for the given SteamID64
	ban_status = await check_ban_status(steamid64)

	if ban_status is None:
		print(f"[WRN] No ban status found for SteamID64: {steamid64}")
		return

	# Step 2: Load the user's data
	data = load_data(user_id)

	# Step 3: Update the 'isBanned' field with the retrieved ban status
	data["isBanned"] = False if ban_status == "No bans detected" else ban_status

	# Step 4: Save the updated data back to the user's JSON file
	save_data(user_id, data)
	print(f"[INF] Updated ban status for user_id {user_id} to: {ban_status}")

async def check_ban_status(user_id, steamid64):
	print(f"[DBG] Checking ban status for SteamID64: {steamid64}")
	url = f"https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={STEAM_API_KEY}&steamids={steamid64}"

	try:
		async with httpx.AsyncClient() as client:
			response = await client.get(url)
			if response.status_code == 200:
				data = response.json()
				if "players" in data and len(data["players"]) > 0:
					player_data = data["players"][0]

					# Determine the ban status
					ban_state = []
					if player_data.get("VACBanned", False):
						ban_state.append("✅ VAC")
					if player_data.get("CommunityBanned", False):
						ban_state.append("✅ Community")
					if player_data.get("EconomyBan", "none") != "none":
						ban_state.append(f"💵 Economy Ban: {player_data['EconomyBan']}")
					if player_data.get("LimitedAccount", False):
						ban_state.append("🔞 Limited Account")
					if player_data.get("NumberOfGameBans", 0) > 0:
						ban_state.append(f"✅ Game Bans: {player_data['NumberOfGameBans']}")

					result = ", ".join(ban_state) if ban_state else "No bans detected"
					print(f"[INF] Ban status: {result}")

					# Step 1: Load the user's data
					data = load_data(user_id)

					# Step 2: Find the account in tracked accounts and update its 'isBanned' field
					for account in data["trackedAccounts"]:
						if account["steamid"] == steamid64:
							account["isBanned"] = False if result == "No bans detected" else result
							print(f"[INF] Updated ban status for SteamID64 {steamid64}: {result}")
							break

					# Step 3: Save the updated data back to the user's JSON file
					save_data(user_id, data)

					return result
	except Exception as e:
		print(f"[ERR] Error checking ban state for SteamID64 {steamid64}: {e}")
	return None

async def get_player_summary(steamid64):
	"""
	Fetches the complete player summary using the Steam API's GetPlayerSummaries endpoint.
	This includes the nickname, profile URL, avatar, real name, and online status.
	"""
	url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={STEAM_API_KEY}&steamids={steamid64}"

	try:
		async with httpx.AsyncClient() as client:
			response = await client.get(url)

			if response.status_code == 200:
				data = response.json()
				if "response" in data and "players" in data["response"]:
					player = data["response"]["players"][0]  # We are only interested in the first player (since we pass one SteamID)

					player_info = {
						"steamid64": steamid64,
						"nickname": player.get("personaname", None),
						"real_name": player.get("realname", None),
						"profile_url": f"https://steamcommunity.com/profiles/{steamid64}/",
						"avatar": player.get("avatarfull", None),
					}

					print(f"[INF] Successfully fetched player summary for SteamID64: {steamid64}")
					return player_info
				else:
					print(f"[WRN] No player data found for SteamID64: {steamid64}")
					return None
			else:
				print(f"[ERR] Failed to fetch data from Steam API: {response.status_code}")
				return None
	except Exception as e:
		print(f"[ERR] Error fetching player summary for SteamID64 {steamid64}: {e}")
		return None