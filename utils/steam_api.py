from utils.load_api_keys import STEAM_API_KEY  # Import steam api key before everything as dummy-check
import re
import requests
from utils.date import from_unix
from utils.logger import debug_print
from utils.data_editor import save_data, load_data
from utils.helpers import sanitize_string, minutes_to_hours
from utils.network import req as network_request, resolve_country_code_for_name as rccfn, follow

async def to_steamid64(input: str):
	if not isinstance(input, int):
		input = input.strip()

	debug_print('debug', f"Received steam account input: {input}")

	# Initialize the steamid64 variable
	steamid64 = None

	# First, check if it's a direct SteamID64 (17 digits)
	# if input.isdigit() and len(input) == 17:
	if isinstance(input, (int, str)) and str(input).isdigit() and len(str(input)) == 17:
		debug_print('info', f"Detected SteamID64 directly: {input}")
		steamid64 = int(input)

	# Check if it's a SteamID3 (format: [U:1:<number>])
	if not steamid64:
		steamid3_pattern = r"\[U:1:(\d+)\]"
		steamid3_match = re.match(steamid3_pattern, input)
		if steamid3_match:
			debug_print('info', f"Matched SteamID3 format: {steamid3_match.group(1)}")
			steamid64 = steamid3_to_steamid64(steamid3_match.group(1))

	# Check if it's a Steam short link
	if not steamid64 and input.startswith("https://s.team/p/"):
		debug_print('debug', f"Detected Steam short link: {input}")
		resolved_url = await follow(input)

		if resolved_url:
			debug_print('info', f"Resolved short link to: {resolved_url}")
			input = resolved_url
		else:
			debug_print('warning', f"Failed to resolve short link: {input}")

	# Check if it's a Steam profile URL
	if not steamid64:
		profile_url_pattern = r"^https?://steamcommunity\.com/profiles/(\d+)/?$"
		profile_url_match = re.match(profile_url_pattern, input)
		if profile_url_match:
			debug_print('info', f"Matched profile URL with SteamID64: {profile_url_match.group(1)}")
			steamid64 = profile_url_match.group(1)

	# Check if it's a custom Steam community URL (with a username)
	if not steamid64:
		custom_url_pattern = r"^https?://steamcommunity\.com/id/([a-zA-Z0-9_]+)/*$"
		debug_print('debug', f"Checking custom URL pattern for: {input}")
		custom_url_match = re.match(custom_url_pattern, input)
		if custom_url_match:
			debug_print('info', f"Matched custom URL: {custom_url_match.group(1)}")
			steamid64 = await resolve_steamid_from_custom_url(custom_url_match.group(1))
			if not steamid64:
				debug_print('warning', f"Failed to resolve custom URL: {input}")

	# No match found or invalid SteamID64
	if steamid64:
		return int(steamid64)

	debug_print('error', f"No match found for input: {input}")
	return None

async def resolve_steamid_from_custom_url(custom_url: str):
	debug_print('debug', f"Resolving SteamID64 from custom URL: {custom_url}")
	URL = f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?key={STEAM_API_KEY}&vanityurl={custom_url}"

	try:
		response = requests.get(URL)

		if response.status_code == 200:
			data = response.json()
			if data.get("response", {}).get("steamid"):
				debug_print('info', f"Resolved SteamID64 from custom URL: {data['response']['steamid']}")
				return data["response"]["steamid"]
			else:
				debug_print('warning', f"Failed to resolve custom URL: {custom_url}")
				return None
		else:
			debug_print('error', f"API response error: {response.status_code}, {response.text}")
			return None
	except requests.exceptions.RequestException as e:
		debug_print('error', f"Error resolving custom URL: {e}")
		return None

def steamid3_to_steamid64(steamid3:str):
	steamid64 = str(int(steamid3) + 76561197960265728)
	debug_print('info', f"Converted SteamID3 to {steamid64}")
	return steamid64

async def get_nickname(steamid64:int, userid:int):
	debug_print('debug', f"Fetching nickname for {steamid64}")
	URL = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={STEAM_API_KEY}&steamids={steamid64}"

	try:
		response = await network_request(URL)

		new_nickname = None
		if response:
			try:
				data = response.json()
				players = data.get("response", {}).get("players", [])
				if players:
					new_nickname = players[0].get("personaname")
					if new_nickname:
						debug_print('info', f"Fetched nickname: {new_nickname}")
			except Exception as e:
				debug_print('error', f"Error parsing Steam API response: {e}")

		data = await load_data(userid)
		tracked_accounts = data.get("trackedAccounts", [])
		stored_nickname = None

		for account in tracked_accounts:
			if account.get("steamid64") == steamid64:
				stored_nickname = account.get("nickname")

				if new_nickname and new_nickname != stored_nickname:
					debug_print('info', f"Updating stored nickname from '{stored_nickname}' to '{new_nickname}'")
					account["nickname"] = new_nickname
					save_data(userid, data)
				break

		final_nickname = new_nickname or stored_nickname
		if final_nickname:
			return sanitize_string(final_nickname)

		debug_print('error', f"No nickname found for {steamid64}")
		return None
	except Exception as e:
		debug_print('error', f"Error fetching nickname for {steamid64}: {e}")

async def check_ban_status(userid:int, steamid64:int, returnAsTable: bool = False):
	debug_print('debug', f"Checking ban status for {steamid64}")
	URL = f"https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={STEAM_API_KEY}&steamids={steamid64}"

	try:
		response = await network_request(URL)

		if response is not None:
			data = response.json()  # Ensure this is valid JSON
			if "players" in data and len(data["players"]) > 0:
				player_data = data["players"][0]

				# Store ban details as a structured dictionary with True/False values
				ban_info = {
					# VAC now has a dictionary with both a bool and a string
					"VAC": False if not player_data.get("VACBanned", False) else {
						"isBanned": True,
						"amount": player_data.get("NumberOfVACBans", 0)
					},
					"community": True if player_data.get("CommunityBanned", False) else False,
					"economy": True if player_data.get("EconomyBan", "none") != "none" else False,
					"isLimited": True if player_data.get("LimitedAccount", False) else False,
					"gameBans": player_data.get("NumberOfGameBans", 0) if player_data.get("NumberOfGameBans", 0) > 0 else False
				}

				# Add 'daysSinceLastBan' only if there is an active ban
				if (isinstance(ban_info["VAC"], dict) and any(ban_info["VAC"].values())) or \
					any(ban_info[key] for key in ["community", "economy", "isLimited", "gameBans"]):
					ban_info["daysSinceLastBan"] = player_data.get("DaysSinceLastBan", 0)  # Use None for clarity

				ban_table = {
					"VAC": ban_info["VAC"],
					"community": ban_info["community"],
					"economy": ban_info["economy"],
					"isLimited": ban_info["isLimited"],
					"gameBans": ban_info["gameBans"]
				}

				if (isinstance(ban_info["VAC"], dict) and any(ban_info["VAC"].values())) or \
					any(ban_info[key] for key in ["community", "economy", "isLimited", "gameBans"]):
					ban_table["daysSinceLastBan"] = player_data.get("DaysSinceLastBan", 0)  # Use None for clarity

				debug_print("info", ban_table)

				if returnAsTable:
					return ban_table

				# Create a formatted ban summary string
				ban_list = []
				if isinstance(ban_info["VAC"], dict) and ban_info["VAC"]["isBanned"]:
					ban_list.append(f"VAC ({ban_info['VAC']['amount']})")
				if ban_info["community"]:
					ban_list.append("Community")
				if ban_info["economy"]:
					ban_list.append("Economy")
				if ban_info["isLimited"]:
					ban_list.append("Limited Account")
				if ban_info["gameBans"]:
					ban_list.append(f"Game Ban ({player_data['NumberOfGameBans']})")

				ban_summary = ", ".join(ban_list) if ban_list else None
				debug_print('info', f"Ban status for {steamid64}: {ban_summary}")

				# Load the user's data
				if not userid:
					debug_print("error", f"no userid provided")
					return None

				data = await load_data(userid)

				# Find the account in tracked accounts and update its 'ban' field
				for account in data["trackedAccounts"]:
					if account["steamid"] == steamid64:
						account["ban"] = ban_info  # Store as dictionary for tracking
						# debug_print('info', f"Updated ban status for {steamid64}: {ban_info}")
						break

				# Save the updated data back to the user's JSON file
				await save_data(userid, data)

				return ban_summary

	except Exception as e:
		debug_print('error', f"Error checking ban status for {steamid64}: {str(e)}")

	return None  # Return None if no valid data or response

async def get_steam_level(steamid64:int):
	URL = f"https://api.steampowered.com/IPlayerService/GetSteamLevel/v1/?key={STEAM_API_KEY}&steamid={steamid64}"

	try:
		response = await network_request(URL)

		if response is not None:
			steam_level_data = response.json()

			# Extract player level (it's in the "player_level" field)
			player_level = steam_level_data.get("response", {}).get("player_level", None)

			if player_level is not None:
				return player_level
			else:
				debug_print('warning', f"Player level not found in response for {steamid64}")
				return None
		else:
			debug_print('error', f"Failed to fetch Steam level data for {steamid64}")
			return None
	except Exception as e:
		debug_print('error', f"Error getting Steam level for {steamid64}: {str(e)}")

async def get_account_summary(steamid64:int, banAsTable:bool=False):
	URL = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={STEAM_API_KEY}&steamids={steamid64}"

	try:
		response = await network_request(URL)

		data = response.json()
		if "response" in data and "players" in data["response"]:
			player = data["response"]["players"][0]

			VISIBILITY_STATES = {
				1: "Private",
				2: "Friends-Only",
				3: "Public"
			}

			COMMENT_PERMISSIONS = {
				0: "Disabled",
				1: VISIBILITY_STATES[1],
				2: VISIBILITY_STATES[2]
			}

			player_info = {
				"steamid64": int(steamid64),
				"nickname": player.get("personaname", None),
				"realName": player.get("realname", None),
				"profileURL": f"https://steamcommunity.com/profiles/{steamid64}/",
				"avatar": {
					"full": player.get("avatarfull", None),
					"medium": player.get("avatarmedium", None),
					"small": player.get("avatar", None),
					"hash": player.get("avatarhash", None),
				},
				"level": await get_steam_level(steamid64),
				"isProfileConfigured": player.get("profilestate", False) == 1,
				"visibility": VISIBILITY_STATES.get(player.get("communityvisibilitystate", 1), None),
				"country": None if await rccfn(player.get("loccountrycode", None)) == "" else await rccfn(player.get("loccountrycode", None)),
				"comments": COMMENT_PERMISSIONS.get(player.get("commentpermission", 0), None),
				"ban": await check_ban_status(None, steamid64, banAsTable),
				"dateCreated": from_unix(player.get("timecreated", 0), True) if player.get("timecreated") else None,
				"games": await get_games_info(steamid64)
			}

			debug_print('info', f"Successfully fetched player summary for {steamid64}")
			return player_info
		else:
			debug_print('warning', f"No player data found for {steamid64}")
			return None
	except Exception as e:
		debug_print('error', f"Failed to fetch data from Steam API for {steamid64}: {e}")

async def get_player_friends(steamid64:int, detailed:bool=True):
	# Construct the URL to get the friend list
	URL = f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={STEAM_API_KEY}&steamid={steamid64}&relationship=all"

	try:
		# Fetch the response from the API
		response = await network_request(URL)

		data = response.json()

		# Check if 'friendslist' is in the response
		if "friendslist" in data and "friends" in data["friendslist"]:
			friends = data["friendslist"]["friends"]  # List of friends

			# Initialize an empty list to store detailed friend info
			detailed_friends = []

			# Loop through each friend and get their summary info
			for friend in friends:
				friend_steamid = friend["steamid"]

				# Fetch the account summary of each friend
				friend_summary = await get_account_summary(friend_steamid, True)

				if friend_summary:
					detailed_friends.append(
						{
							"steamid": int(friend_steamid),
							"nickname": friend_summary.get("nickname"),
							"name": friend_summary.get("realName"),
							"url": friend_summary.get("profileURL"),
							"avatar": {
								"full": friend_summary["avatar"]["full"],
								"medium": friend_summary["avatar"]["medium"],
								"small": friend_summary["avatar"]["small"],
								"hash": friend_summary["avatar"]["hash"],
							},
							"lvl": friend_summary.get("level"),
							"isProfileConfigured": friend_summary.get("isProfileConfigured"),
							"visibility": friend_summary.get("visibility"),
							"country": friend_summary.get("country"),
							"comments": friend_summary.get("comments"),
							"ban": friend_summary.get("ban"),
							"dateCreated": friend_summary.get("dateCreated"),
							"games": friend_summary.get("games"),
							"friendSince": from_unix(friend.get("friend_since", 0), True) if friend.get("friend_since") else None,
						}
					)

			# Return the list of detailed friends
			debug_print('info', f"Successfully fetched detailed friends for {steamid64}")
			return detailed_friends
		else:
			debug_print('warning', f"No friends found for {steamid64}")
			return None
	except Exception as e:
		debug_print('error', f"Failed to fetch data from Steam API for friends list for {steamid64}: {e}")

async def get_games_info(steamid64:int):
	URL = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_API_KEY}&steamid={steamid64}&format=json"

	try:
		# Fetch the response from the API
		response = await network_request(URL)
		data = response.json()

		# Log the response data to see what we are getting
		# debug_print('info', f"Steam API Response: {data}")

		# List of games to look for
		games2Look = {
			"CoD": {
				"MW 2": 10180,
				"MW 3": 42680,
				"BO 2": 202970,
				"Ghosts": 209160,
				"AW": 209660,
				"IW": 292730,
				"WW2": 476600,
				"BO 4": 594650,
				"HQ": 1938090,
				"Warzone": 1962663
			},
			"BF": {
				"1": 1238840,
				"5": 1238810,
				"2042": 1517290,
			},
			"Dota 2": 570,
			"CS2": 730,
			"Rust": 252490,
			"PUBG": 578080,
			"R6 Siege": 359550,
			"Apex Legends": 1172470,
		}

		# Check if the response contains the games data
		if "response" in data and "games" in data["response"]:
			game_count = data["response"]["game_count"]  # Get total number of games
			games = data["response"]["games"]
			game_info = {}  # Dictionary to store info for each game franchise

			# Iterate through the list of games to find each game in games2Look
			for franchise, game_versions in games2Look.items():
				# If franchise is a dictionary (e.g. CoD or BF), loop through its versions
				if isinstance(game_versions, dict):
					for version_name, appid in game_versions.items():
						# Look for the game in the response
						game_found = next((game for game in games if game.get("appid") == appid), None)

						# Debugging: print out what's being checked
						debug_print('info', f"Checking for game {franchise} {version_name} (AppID: {appid})")
						if game_found:
							debug_print('info', f"Found {franchise} {version_name} (AppID: {appid})")
							# Retrieve playtime and last played info
							playtime = minutes_to_hours(game_found.get("playtime_forever", 0))  # Convert minutes to hours
							last_played = None  # Variable to store last played time if available
							if "rtime_last_played" in game_found:
								last_played = from_unix(game_found["rtime_last_played"], True)

							# Skip games that have no playtime or last played info
							if playtime is None or playtime <= 0:
								continue

							# Ensure the franchise is in the game_info dictionary
							if franchise not in game_info:
								game_info[franchise] = {}

							# Add the game info to the dictionary under the franchise and version
							game_info[franchise][version_name] = {
								"playtime": playtime,
								"lastPlayed": last_played
							}
				else:
					# If the game is not a franchise with versions (like Dota 2, CS2), handle it separately
					appid = game_versions
					# Look for the game in the response
					game_found = next((game for game in games if game.get("appid") == appid), None)

					# Debugging: print out what's being checked
					debug_print('info', f"Checking for game {franchise} (AppID: {appid})")
					if game_found:
						debug_print('info', f"Found {franchise} (AppID: {appid})")
						# Retrieve playtime and last played info
						playtime = minutes_to_hours(game_found.get("playtime_forever", 0))  # Convert minutes to hours
						last_played = None  # Variable to store last played time if available
						if "rtime_last_played" in game_found:
							last_played = from_unix(game_found["rtime_last_played"], True)

						# Skip games that have no playtime or last played info
						if playtime is None or playtime <= 0:
							continue

						# Add the game info to the dictionary under the franchise (game name is the franchise)
						if franchise not in game_info:
							game_info[franchise] = {}

						game_info[franchise] = {
							"playtime": playtime,
							"lastPlayed": last_played
						}

			# Return a summary table with owned games and individual game info
			table = {
				"owned": game_count,
				"games": game_info
			}

			return table  # Return the games info dictionary

		debug_print('info', f"No games found for Steam ID {steamid64}")
		return None

	except Exception as e:
		debug_print('error', f"Failed to fetch data from Steam API for games list for {steamid64}: {e}")
		return None

async def write_account_summary(userid:int, steamid64:int, includeFriends=False):
	# Load existing data for the user
	data = await load_data(userid)

	# Fetch player summary details
	player_summary = await get_account_summary(steamid64)

	# Fetch friends only if includeFriends is True
	if includeFriends:
		friends = await get_player_friends(steamid64)
	else:
		# Keep the existing friends data from the loaded data if includeFriends is False
		existing_account = next((account for account in data.get("trackedAccounts", []) if account["steamid"] == steamid64), None)
		if existing_account:
			friends = existing_account.get("friends", None)
		else:
			friends = None

	if player_summary is None:
		return

	# Create the account info to be added/updated
	account_info = {
		"steamid": int(steamid64),
		"nickname": player_summary["nickname"],
		"name": player_summary["realName"],
		"url": player_summary["profileURL"],
		"avatar": {
			"full": player_summary["avatar"]["full"],
			"medium": player_summary["avatar"]["medium"],
			"small": player_summary["avatar"]["small"],
			"hash": player_summary["avatar"]["hash"],
		},
		"lvl": player_summary["level"],
		"isProfileConfigured": player_summary["isProfileConfigured"],
		"visibility": player_summary["visibility"],
		"country": player_summary["country"],
		"comments": player_summary["comments"],
		"ban": player_summary["ban"],
		"dateCreated": player_summary["dateCreated"],
		"games": player_summary["games"]
	}

	# Add friends to the account info if includeFriends is True
	if includeFriends and friends:
		account_info["friends"] = friends

	# Ensure 'trackedAccounts' is a list
	if "trackedAccounts" not in data:
		data["trackedAccounts"] = []

	# Check if the account exists
	existing_account = next((account for account in data["trackedAccounts"] if account["steamid"] == steamid64), None)

	if existing_account:
		# Update only if there are changes
		if existing_account != account_info:
			debug_print('info', f"Updating account {steamid64} with new details.")
			existing_account.update(account_info)  # Modify existing account in place
		else:
			debug_print('info', f"No changes detected for account {steamid64}.")
	else:
		# Add new account
		data["trackedAccounts"].append(account_info)
		debug_print('info', f"Added new account {steamid64} to tracked accounts.")

	# debug_print('info', data)

	# Save the updated data back to the file
	await save_data(userid, data)