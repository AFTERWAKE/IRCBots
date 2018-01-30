# pointBot
This is a simple IRC bot that uses the twisted IRC client. It keeps track of points given to users, which are given
through traditional +1, -1, etc. Each user gets 10 "gift points" to pass out every calendar day.

ADMIN COMMANDS
	 pointBot, reset (refreshes user gift point totals)
	 pointBot, save (saves list of winners || also gets saved at the end of every day)
	 pointBot, restore (restores winners from save file || also restores automatically on run)
	 pointBot, say <msg> (sends message to channel as the bot)
	 pointBot, ignore <nick> (adds user to the ignore list; removes from game)
	 pointBot, unignore <nick>
	 pointBot, set <nick> <points> (set points for user)
	 pointBot, del <nick> (delete a user from the points table)
	 
USER COMMANDS
	 pointBot, help (command list)
	 pointBot, rules (bot introduction)
	 pointBot, scores (list of active players and scores)
	 pointBot, unsub (adds user to the ignore list)
	 +/-<pts> to <nick> [reason]