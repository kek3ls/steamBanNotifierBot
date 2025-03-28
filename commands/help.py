from telegram import Update
from utils.logger import debug_print
from telegram.ext import CallbackContext

async def help_command(update: Update, context: CallbackContext) -> None:
	userid = update.message.from_user.id

	debug_print("debug", f"help command requested by {userid}")

	if context.args:
		command: str = context.args[0]  # 0 is for argument number if more than 1 provided
		# command_arguments = context.args[1]

		steamid_formats = "• <b>SteamID64</b> (64-bit ID): <code>12345678909876543</code>\n" \
					"• <b>SteamID3</b> (Account ID): <code>[U:1:23456789]</code>\n" \
					"• <b>Steam short link</b>: <code>https://s.team/p/abcd-dcba</code>\n" \
					"• <b>Steam permanent link</b>: <code>https://steamcommunity.com/profiles/12345678909876543</code>\n" \
					"• <b>Steam custom link</b>: If a user has set a custom URL for their profile, e.g., <code>https://steamcommunity.com/id/username</code>"

		command_help = {
			"add": "Adds a Steam account to your tracking list.\n\n"
				"This allows the bot to monitor the account for ban status changes and notify you if any occur.\n\n"
				"You can provide the Steam ID in various formats:\n"
				+ steamid_formats + "\n\n"
				"Usage:\n"
				"<code>/add &lt;input&gt;</code>\n\n"
				"Parameters:\n"
				"🔹 <b>steam account input</b> - Any supported steam account input.\n\n"
				"Example:\n"
				"<code>/add 12345678909876543</code> - Adds this Steam account to your tracking list.\n\n"
				"Note:\n"
				"✅ You can track up to <b>10 accounts</b> at a time.\n"
				"✅ If the account is already being tracked, the bot will notify you.\n"
				"⚠️ If you have reached the limit, you must remove an account before adding a new one.",

			"remove": "Removes a Steam account from your tracking list.\n\n"
				"If you no longer want to track a specific Steam account, use this command to remove it.\n\n"
				"You can provide the Steam ID in various formats:\n"
				+ steamid_formats + "\n\n"
				"Usage:\n"
				"<code>/remove &lt;input&gt;</code>\n\n"
				"Parameters:\n"
				"🔹 <b>steam account input</b> - Any supported steam account input.\n\n"
				"Example:\n"
				"<code>/remove 12345678909876543</code> - Removes this Steam account from your tracking list.\n\n"
				"Note:\n"
				"⚠️ If the account is not in your tracking list, the bot will notify you.",

			"list": "Displays all Steam accounts you are currently tracking.\n\n"
				"This helps you keep track of the accounts you’ve added for monitoring.\n\n"
				"Usage:\n"
				"<code>/list</code>\n\n"
				"Example:\n"
				"<code>/list</code> - Shows all Steam accounts you are tracking.\n\n"
				"Note:\n"
				"✅ If your tracking list is empty, the bot will notify you.",

			"flush": "Manually triggers a data update for all your tracked accounts.\n\n"
				"This forces the bot to check the ban status of all Steam accounts you are tracking immediately,\n"
				"instead of waiting for the automatic interval.\n\n"
				"Usage:\n"
				"<code>/flush</code>\n\n"
				"Example:\n"
				"<code>/flush</code> - Manually checks the ban status of all tracked accounts.\n\n"
				"Note:\n"
				"✅ This command does not affect automatic checks.\n"
				"✅ Useful when you suspect a ban has occurred but haven’t received a notification yet.",

			"startbancheck": "Enables automatic ban status checks every 6 hours.\n\n"
				"Once enabled, the bot will periodically check all tracked accounts and notify you of any bans.\n\n"
				"Usage:\n"
				"<code>/startbancheck</code>\n\n"
				"Example:\n"
				"<code>/startbancheck</code> - Activates automatic ban status monitoring.\n\n"
				"Note:\n"
				"✅ Default check interval is 6 hours (can be changed with /interval).\n"
				"✅ You can still manually check with /flush.",

			"startbc": "Alias for /<b>startbancheck</b>. Does the same thing.\n\n"
				"Usage:\n"
				"<code>/startbc</code>",

			"stopbancheck": "Stops the automatic ban status checks.\n\n"
				"If you no longer want the bot to automatically check for bans, use this command.\n\n"
				"Usage:\n"
				"<code>/stopbancheck</code>\n\n"
				"Example:\n"
				"<code>/stopbancheck</code> - Disables automatic ban status monitoring.\n\n"
				"Note:\n"
				"✅ You will still be able to check manually using /flush.\n"
				"✅ You can restart automatic checks anytime using /startbancheck.",

			"stopbc": "Alias for /<b>stopbancheck</b>. Does the same thing.\n\n"
				"Usage:\n"
				"<code>/stopbc</code>",

			"interval": "Adjusts the interval for automatic ban status checks.\n\n"
				"By default, the bot checks for bans every 6 hours, but you can change this to fit your needs.\n"
				"Setting a shorter interval means more frequent updates, while a longer interval reduces the frequency of checks.\n\n"
				"Usage:\n"
				"<code>/interval &lt;hours&gt;</code>\n\n"
				"Parameters:\n"
				"🔹 <b>hours</b> - The time in hours between each automatic ban check. Must be a positive integer.\n\n"
				"Example:\n"
				"<code>/interval 3</code> - Sets the ban check interval to every 3 hours.\n"
				"<code>/interval 12</code> - Sets the ban check interval to every 12 hours.\n\n"
				"Note:\n"
				"⚠️ Setting an interval that is too short (e.g., 1 hour) may result in unnecessary spam.\n"
				"⚠️ The bot may enforce a minimum or maximum interval limit to prevent abuse."
		}

		response = command_help.get(command, f"Unknown command: {command}. Use /<b>help</b> to see available commands.")

		await update.message.reply_text(response, parse_mode="HTML")
		debug_print("info", f"help_{command} sent to {userid}")
		return

	await update.message.reply_text(
		"👋 <b>Welcome</b> to the <b>Help Section</b>! 🎉\n\n"
		"Before using the bot, we recommend taking a moment to read our "
		"<a href='https://steambannotifierbot.k3ls.ru/privacyPolicy'><b>Privacy Policy</b></a> "
		"to learn about how <b>your data is collected</b> and managed. 🔒\n\n"
		"Please note that the /<b>start</b> and /<b>help</b> commands <b>do not</b> collect any personal data."
		"You can freely use these commands to explore available features without concern. 📝🚀\n\n"
		"📚 <b>Here’s what I can do for you</b>:\n"
		"🔹 /<b>start</b> - Start interacting with the bot.\n"
		"🔹 /<b>help</b> [<b>add</b>, <b>remove</b>, <b>list</b>, <b>flush</b>, <b>startbancheck</b>, <b>startbc</b>, <b>stopbancheck</b>, <b>stopbc</b>, <b>interval</b>] - Display this helpful guide. If a command provided as an argument, it will display detailed help about the command.\n"
		"🔹 /<b>add</b> &lt;<b>SteamID64</b>, <b>SteamID3</b>, <b>Steam short link</b>, <b>Steam permanent link</b>, <b>Steam custom link</b>&gt; - Add a Steam account to tracking accounts.\n"
		"🔹 /<b>remove</b> &lt;<b>SteamID64</b>, <b>SteamID3</b>, <b>Steam short link</b>, <b>Steam permanent link</b>, <b>Steam custom link</b>&gt; - Remove a Steam account from your tracking accounts.\n"
		"🔹 /<b>list</b> - View all your tracked Steam accounts.\n"
		"🔹 /<b>flush</b> - Check the ban status of your tracked accounts.\n"
		"🔹 /<b>startbancheck</b> or /<b>startbc</b> - Start automatic ban checks every 6 hours for your accounts.\n"
		"🔹 /<b>stopbancheck</b> or /<b>stopbc</b> - Stop the automatic ban checks.\n"
		"🔹 /<b>interval</b> &lt;<b>hours</b>&gt; - Adjust the interval for automatic ban checks.\n\n"
		"Need more help or want to contact support? Visit here: <a href='https://k3ls.ru/'><b>Support Link</b></a>.\n\n"
		,parse_mode="HTML" # keep the comma before "parse_mode" in case of adding any more lines
	)

	debug_print("info", f"help sent to {userid}")