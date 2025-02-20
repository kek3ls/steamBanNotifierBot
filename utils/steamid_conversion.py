import re
import requests
from utils.load_api_keys import STEAM_API_KEY

async def convert_to_steamid64(input_str):
	input_str = input_str.strip()

	# Check if it's a Steam short link
	if input_str.startswith("https://s.team/p/"):
		resolved_url = await resolve_steam_shortlink(input_str)
		if resolved_url:
			input_str = resolved_url  # Replace input with resolved URL

	print(f"Received input: {input_str}")  # Debug print

	# Try to match if it's a profile URL (either with or without https://)
	profile_url_pattern = r"^https?://steamcommunity\.com/profiles/(\d+)/?$"
	profile_url_match = re.match(profile_url_pattern, input_str)
	if profile_url_match:
		print(f"Matched profile URL with SteamID64: {profile_url_match.group(1)}")  # Debug print
		# It's a SteamID64 (permanent profile URL), return the matched SteamID64
		return profile_url_match.group(1)

	# Try to match if it's a custom URL (e.g., steamcommunity.com/id/customURL)
	custom_url_pattern = r"^https?://steamcommunity\.com/id/([a-zA-Z0-9_]+)/*$"
	print(f"Checking custom URL pattern for: {input_str}")  # Debug print before match
	custom_url_match = re.match(custom_url_pattern, input_str)
	if custom_url_match:
		print(f"Matched custom URL: {custom_url_match.group(1)}")  # Debug print
		custom_url = custom_url_match.group(1)
		return await resolve_steamid_from_custom_url(custom_url)
	else:
		print(f"Custom URL match failed for: {input_str}")

	# If it's already a SteamID64 (17-digit number), return it
	if input_str.isdigit() and len(input_str) == 17:
		print(f"Detected SteamID64 directly: {input_str}")  # Debug print
		return input_str

	# If it's SteamID3 format, resolve it to SteamID64
	steamid3_pattern = r"\[U:1:(\d+)\]"
	steamid3_match = re.match(steamid3_pattern, input_str)
	if steamid3_match:
		print(f"Matched SteamID3 format: {steamid3_match.group(1)}")  # Debug print
		return steamid3_to_steamid64(steamid3_match.group(1))

	print(f"No match found for input: {input_str}")  # Debug print
	return None

async def resolve_steam_shortlink(short_url):
	try:
		response = requests.get(short_url, allow_redirects=True)
		if response.status_code == 200:
			final_url = response.url  # Get the final redirected URL
			print(f"Resolved short link to: {final_url}")  # Debug print
			return final_url
		else:
			print(f"Failed to resolve short link: {response.status_code}")
			return None
	except requests.exceptions.RequestException as e:
		print(f"Error resolving short link: {e}")
		return None

async def resolve_steamid_from_custom_url(custom_url):
	print(f"Resolving SteamID64 from custom URL: {custom_url}")  # Debug print
	url = f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?key={STEAM_API_KEY}&vanityurl={custom_url}"
	try:
		response = requests.get(url)
		if response.status_code == 200:
			data = response.json()
			if data.get("response", {}).get("steamid"):
				print(f"Resolved SteamID64 from custom URL: {data['response']['steamid']}")  # Debug print
				return data["response"]["steamid"]
			else:
				print(f"Failed to resolve custom URL: {custom_url}")  # Debug print
				return None
		else:
			print(f"Error in API response: {response.status_code}, {response.text}")  # Debug print
			return None
	except requests.exceptions.RequestException as e:
		print(f"Error resolving custom URL: {e}")  # Debug print
		return None

def steamid3_to_steamid64(steamid3):
	steamid64 = str(int(steamid3) + 76561197960265728)
	print(f"Converted SteamID3 to SteamID64: {steamid64}")  # Debug print
	return steamid64