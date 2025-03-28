from datetime import datetime, timedelta

def from_unix(timestamp: float, includeTimestamp:bool=False):
	"""Converts a Unix timestamp to an ISO 8601 formatted string."""
	return convert(datetime.utcfromtimestamp(timestamp).isoformat() if timestamp else None, includeTimestamp)

def to_unix(iso_string: str):
	"""Converts an ISO 8601 formatted string to a Unix timestamp."""
	return int(datetime.fromisoformat(iso_string).timestamp())

def convert(iso_string: str, includeTimestamp:bool=False):
	"""Converts an ISO 8601 formatted string to a formatted date.

	If includeTimestamp=True, returns full datetime (YYYY-MM-DD HH:MM:SS).
	Otherwise, returns only the date (YYYY-MM-DD).
	"""
	dt = datetime.fromisoformat(iso_string)
	format_str = '%Y-%m-%d %H:%M:%S' if includeTimestamp else '%Y-%m-%d'
	return dt.strftime(format_str)

def to_human(iso_string: str, includeTimestamp:bool=False):
	"""Converts an ISO 8601 formatted string to a human-readable date.

	If includeTimestamp=True, returns full datetime (DD.MM.YYYY HH:MM:SS).
	Otherwise, returns only the date (DD.MM.YYYY).
	"""
	dt = datetime.fromisoformat(iso_string)
	format_str = '%d.%m.%Y %H:%M:%S' if includeTimestamp else '%d.%m.%Y'
	return dt.strftime(format_str)

def to_rfc2822(iso_string: str, includeTimestamp:bool=False):
	"""Converts an ISO 8601 formatted string to an RFC 2822 formatted date.

	If includeTimestamp=True, includes the full time.
	Otherwise, returns a shorter version without time.
	"""
	dt = datetime.fromisoformat(iso_string)
	format_str = '%a, %d %b %Y %H:%M:%S +0000' if includeTimestamp else '%a, %d %b %Y'
	return dt.strftime(format_str)