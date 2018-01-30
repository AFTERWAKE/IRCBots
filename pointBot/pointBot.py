'''
--------------------------------------------------------------------------------------------------------------------
 Author: jlong
 Date: January 2018
 Description: This connects to an IRC channel and keeps track of arbitrary points given out by other users.
 
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
--------------------------------------------------------------------------------------------------------------------
'''
from twisted.words.protocols import irc
from datetime import datetime
from re import match
from sys import exit

class player:
	totalScore = 0
	giftPoints = 10
	nick = ""
	host = ""

	def __init__(self, nick, host):
		self.nick = nick
		self.host = host

class pointBot(irc.IRCClient):
	nickname = "pointBot"
	channel = "#main"
	testing = False
	pointsFilePath = ".\points.txt"
	ignoreFilePath = ".\ignore.txt"
	gameRunning = False
	userList = []
	ignoreList = []
	adminNick = "jlong"
	adminHost = "172.22.116.14"

	def __init__(self):
		self.restore()
		self.resetGame()

	"""
	Twisted IRC Client Methods
	"""

	# Called when bot joins the IRC network
	def signedOn(self):
		self.join(self.channel)
	
	# Called when a PM is sent to the bot or to a channnel on the network
	# We use this to add someone to the game whenever they first send a message
	#  as well as handle admin/user commands and point exchanges.
	def privmsg(self, user, channel, message):
		# Accept admin PMs or messages on our channel
		if ((channel == self.channel) or (user.split('@')[1] == self.adminHost)):
			hour = int(self.getCurrentHour())
			# Run the game from 8 AM to 5 PM and refresh gift points in the morning
			if (hour >= 8 and hour < 17):
				if not self.gameRunning:
					self.resetGame()
			elif self.gameRunning:
				self.stopGame()
				self.save()
			print ("{}: {}".format(user, message))
			nick = user.split('!')[0]
			host = user.split('@')[1]
			if nick in self.ignoreList:
				return
			self.addUserIfNew(nick, host)
			if (message.startswith(self.nickname + ", ")):
				if (host == self.adminHost):
					self.adminCommands(message.split(", ")[1])
				else:
					self.userCommands(nick, message.split(", ")[1])
			elif message.startswith('+') or message.startswith('-'):
				self.pointMessage(nick, message)
		else:
			print user
		return
	
	# Called when a user joins the channel. Currently used for auto-kick when testing :)
	def userJoined(self, user, channel):
		if (user != self.adminNick and self.testing):
			self.kick(channel, user, reason="I'm testing, please do not disturb :^)")
		return
	
	# Called when a user changes their nick. Updates their user list entry.
	def userRenamed(self, oldname, newname):
		index = self.getUserIndex(oldname)
		if (index != -1):
			self.userList[index].nick = newname
		return
		
	"""
	Command Lists
	"""
	def adminCommands(self, message):
		print(message)
		if (message == "admin"):
			self.msg(self.channel, "admin")
		elif (message == "reset"):
			self.resetGame()
		elif (message == "save"):
			self.save()
		elif (message == "restore"):
			self.restore()
		elif (message.startswith("say ")):
			self.msg(self.channel, message.split("say ")[1])
		elif (message.startswith("ignore ")):
			self.ignoreUser(message.split(" ")[1])
		elif (message.startswith("unignore ")):
			self.unignoreUser(message.split(" ")[1])
		elif (message.startswith("set ")):
			setMsg = message.split(" ")
			self.setUserScore(setMsg[1], setMsg[2])
		elif (message.startswith("del ")):
			self.delUser(message.split(" ")[1])
		else:
			self.userCommands(self.adminNick, message)
		return
		
	def userCommands(self, nick, message):
		if (message == "help"):
			print("Admin Commands: reset, save, restore, ignore <user>, unignore <user>, set <user> <score>, say <msg>")
			self.msg(self.channel, "User Commands: help, rules, scores, unsub [e.g. pointBot, help]")
			self.msg(self.channel, "Point Exchanges: +/-<pts> to <user> [reason] (e.g. +1 to pointBot for being awesome)")
		elif (message == "rules"):
			self.msg(self.channel, "Hello, it's me, pointBot. I keep track of +s and -s handed out in the IRC. " +
                 "You get 10 points to give away every day, and these points are refreshed every morning at 8 AM. " +
                 "Using bots is not allowed. If you run into any issues, talk to the admin (J. Long). " +
                 "Have a day.")
		elif (message == "scores"):
			self.displayScores()
		elif (message == "unsub"):
			self.ignoreUser(nick)
		return
		
	"""
	Command Functions
	"""
	# Restores user/score list and ignore list from files; called on startup or from admin command
	def restore(self):
		try:
			self.userList = []
			pointsFile = open(self.pointsFilePath, 'r')
			users = pointsFile.readlines()
			for user in users:
				userString = user.split(':')
				self.userList.append(player(userString[0], userString[1]))
				self.userList[-1].totalScore = int(userString[2].rstrip())
			pointsFile.close()
			print("Scores restored.")
		except:
			print("Restore failed.")
			exit("Score restore fail")
		
		try:
			self.ignoreList = []
			ignoreFile = open(self.ignoreFilePath, 'r')
			ignored = ignoreFile.readlines()
			for ignore in ignored:
				self.ignoreList.append(ignore.split('\n')[0])
			ignoreFile.close()
			print("Ignore file restored.")
		except:
			print("Restore failed.")
			exit("Ignore restore fail")
		return
	
	# (Admin command) Saves user scores and ignore list to files; called at the end of every day
	def save(self):
		pointsFile = open(self.pointsFilePath, 'w')
		for i in range(len(self.userList)):
			pointsFile.write("{}:{}:{}\n".format(self.userList[i].nick, self.userList[i].host, str(self.userList[i].totalScore)))
		pointsFile.close()
		print("Scores saved.")
		
		ignoreFile = open(self.ignoreFilePath, 'w')
		for ignore in self.ignoreList:
			ignoreFile.write(ignore + "\n")
		ignoreFile.close()
		print("Ignore list saved.")
		return
	
	# (Admin command) Resets gift points and starts the game; called at the beginning of every day and on startup
	def resetGame(self):
		self.gameRunning = True
		for i in range(len(self.userList)):
			self.userList[i].giftPoints = 10
		print("The game has been reset. Gift points have been restored.")
		return
	
	# (Admin command) Stops the game; called at the end of every day 
	def stopGame(self):
		self.gameRunning = False
		print("The game has been stopped.")
		return
	
	# (Admin command) Sets a user's score
	def setUserScore(self, nick, score):
		index = self.getUserIndex(nick)
		if (index == -1):
			print("Invalid username.")
			return
		self.userList[index].totalScore = int(score)
		return
	
	# (Admin/user command) Ignores a user (pointBot ignores all messages from this user, ignores point exchanges, hides from score display if they are past player)
	def ignoreUser(self, nick):
		if nick not in self.ignoreList:
			self.ignoreList.append(nick)
		return
	
	# (Admin command) Unignores a user
	def unignoreUser(self, nick):
		if nick in self.ignoreList:
			self.ignoreList.remove(nick)
		return
	
	# (User command) Displays scores
	def displayScores(self):
		self.msg(self.channel, "Here is a list of scores in the format \'User: Points\'")
		scoreList = ""
		for user in self.userList:
			if user.nick not in self.ignoreList:
				scoreList += "{}: {} ".format(user.nick, user.totalScore)
		self.msg(self.channel, scoreList)
		return
		
	# (User command) Exchanges points between two players
	def pointMessage(self, sender, message):
		if self.gameRunning:
			# Message format: +/-<pts> to <user> [reason]
			validMsg = match('^(\+|-)(\d+) to (\w+)(\W+(.*))?$', message)
			if validMsg is not None:
				sign = validMsg.group(1)
				number = validMsg.group(2)
				target = validMsg.group(3)
				reason = validMsg.group(5)
				
				# No self-points, and can't send more gift points than you currently have
				senderIndex = self.getUserIndex(sender)
				if self.userList[senderIndex].nick == target:
					self.msg(sender, "Nice try, dingus")
					return
				if self.userList[senderIndex].giftPoints <= 0:
					self.msg(sender, "You are out of gift points for the day! No points exchanged.")
					return
				if self.userList[senderIndex].giftPoints < int(number):
					self.msg(sender, "You only have " + str(self.userList[userIndex].giftPoints) + " gift points remaining! No points exchanged.")
					return
				
				# Can't send to a user who isn't in the game or has been ignored
				targetIndex = self.getUserIndex(target)
				if (targetIndex == -1) or (self.userList[targetIndex].nick in self.ignoreList):
					self.msg(sender, "User " + target + " is not in the game. No points exchanged.")
					return
					
				if sign == '+':
					self.userList[targetIndex].totalScore += int(number)
				else:
					self.userList[targetIndex].totalScore -= int(number)
				self.userList[senderIndex].giftPoints -= int(number)
				
				self.msg(sender, "You have gifted " + sign + number + " points to " + target + ". You have " + str(self.userList[senderIndex].giftPoints) + " gift points left for the day.")
				targetString = "You have been gifted " + sign + number + " points by " + sender + "."
				if reason != "":
					targetString += " Reason: \"" + reason + "\""
				targetString += " You now have " + str(self.userList[targetIndex].totalScore) + " total points."
				self.msg(target, targetString)
		else:
			self.msg(sender, "The point game is not running right now.")
		return
		
	"""
	Utility Functions
	"""
	# Gets index of user in user list
	def getUserIndex(self, nick):
		for i in range(len(self.userList)):
			if (self.userList[i].nick == nick):
				return i
		return -1
	
	# Points are tied to the host to track past nick changes, so check to see if host is in list first; if not, add new player
	def addUserIfNew(self, nick, host):
		for i in range(len(self.userList)):
			if (self.userList[i].host == host):
				self.userList[i].nick = nick
				return
		self.userList.append(player(nick, host))
		return
				
	@staticmethod
	def getCurrentHour():
		time = match('^(\d+):\d+', str(datetime.now().time()))
		return time.group(1)