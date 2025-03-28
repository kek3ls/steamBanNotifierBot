import httpx
import asyncio
from utils.logger import debug_print

async def req(url: str, retries: int = 3, delay: int = 5):
	attempt = 0
	while attempt < retries:
		try:
			async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
				response = await client.get(url)

				if response.status_code == 200:
					return response

				elif response.status_code == 429:  # Too Many Requests
					retry_after = int(response.headers.get("Retry-After", delay))
					debug_print("warning", f"Rate limited! Retrying after {retry_after}s")
					await asyncio.sleep(retry_after)  # Use Retry-After, do NOT add another sleep!

				elif response.status_code >= 500:  # Server Errors
					debug_print("warning", f"Server error {response.status_code}. Retrying...")

				else:
					debug_print("error", f"Request failed with status {response.status_code}")
					return None

		except httpx.ConnectTimeout:
			debug_print("error", "Connection timeout! Retrying with a longer delay...")
			await asyncio.sleep(delay * 2)  # Double the delay on timeout

		except Exception as e:
			debug_print("error", f"Request failed: {e}")

		attempt += 1
		if attempt < retries:
			debug_print("debug", f"Retrying... ({attempt}/{retries}) after {delay}s")
			await asyncio.sleep(delay)  # Only one sleep statement here

	debug_print("error", f"Failed to retrieve data after {retries} attempts.")
	return None

async def follow(url: str, retries: int = 3, delay: int = 5):
	"""Follows redirects for a given URL safely, with retries and rate limit handling."""
	attempt = 0
	while attempt < retries:
		try:
			async with httpx.AsyncClient(timeout=httpx.Timeout(15.0), follow_redirects=True) as client:
				response = await client.get(url)

				if response.status_code == 200:
					final_url = str(response.url)
					debug_print("info", f"Final URL after redirects: {final_url}")
					return final_url

				elif response.status_code == 429:  # Too Many Requests
					retry_after = int(response.headers.get("Retry-After", delay))
					debug_print("warning", f"Rate limited! Retrying after {retry_after}s")
					await asyncio.sleep(retry_after)

				elif response.status_code >= 500:  # Server Errors
					debug_print("warning", f"Server error {response.status_code}. Retrying...")

				else:
					debug_print("error", f"Request failed with status {response.status_code}")
					return None

		except httpx.ConnectTimeout:
			debug_print("error", "Connection timeout! Retrying with a longer delay...")
			await asyncio.sleep(delay * 2)

		except Exception as e:
			debug_print("error", f"Request failed: {e}")

		attempt += 1
		if attempt < retries:
			debug_print("debug", f"Retrying... ({attempt}/{retries}) after {delay}s")
			await asyncio.sleep(delay)

	debug_print("error", f"Failed to resolve URL after {retries} attempts.")
	return None

async def resolve_country_code_for_name(code: str):
	"""Returns country name from country code. Example: LV to Latvia"""
	if not code or code == "":
		return ""

	URL = f"https://restcountries.com/v3.1/alpha/{code}"

	response = await req(URL)  # Make an async HTTP request to get the data
	data = response.json()  # Parse the JSON response

	# Extract the 'common' name from the response
	if data:  # Check if data is not empty
		return data[0]['name']['common']
	else:
		return ""  # If no data is returned, return an empty string