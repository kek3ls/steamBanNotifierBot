import re

def sanitize_string(input: str):
	if not isinstance(input, str):
		raise ValueError("Input must be a string")

	# Define the regex pattern for sanitizing
	pattern = re.compile(r'[^\w\s\u4e00-\u9fff\u0400-\u04FF\u0300-\u036f\u2000-\u206f\u2e00-\u2e7f\u2500-\u257f\u2600-\u26FF\u2700-\u27BF\u00A0-\u00FF\u2B50★]')

	# Return sanitized string
	return pattern.sub('', input)

def minutes_to_days(minutes: int):
	minutes_in_day = 24 * 60  # 1440 minutes in a day
	minutes_in_hour = 60  # 60 minutes in an hour

	# Calculate days, hours, and remaining minutes
	days = minutes // minutes_in_day
	minutes %= minutes_in_day

	hours = minutes // minutes_in_hour
	minutes %= minutes_in_hour

	# Build a human-readable string
	parts = []
	if days > 0:
		parts.append(f"{days} days")
	if hours > 0:
		parts.append(f"{hours} hours")
	if minutes > 0:
		parts.append(f"{minutes} minutes")

	# Return the formatted string
	return ", ".join(parts) if parts else "0 minutes"

def minutes_to_hours(minutes: int):
	minutes_in_hour = 60  # 60 minutes in an hour

	# Calculate total hours
	hours = minutes // minutes_in_hour

	# Return the result as an integer (only hours)
	return hours