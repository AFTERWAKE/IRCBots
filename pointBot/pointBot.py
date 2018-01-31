'''
--------------------------------------------------------------------------------------------------------------------
 Author: jlong
 Date: January 2018
 Description: This connects to an IRC channel and keeps track of arbitrary points given out by other users.
--------------------------------------------------------------------------------------------------------------------
'''
from twisted.words.protocols import irc
from datetime import datetime
from re import match
from sys import exit

class player:
	totalPoints = 0
	giftPoints = 10
	nick = ""
	ip = ""

	def __init__(self, nick, ip):
		self.nick = nick
		self.ip = ip
		
class pointBot(irc.IRCClient):
	# IRC info
	nickname = "pointBot"
	channel = "#main"
	adminNick = "jlong"
	adminIP = "172.22.116.14"
	
	# Game state
	testing = False
	gameRunning = False
	autoMode = False
	
	# Restore file/user info
	pointsFilePath = ".\\points.txt"
	ignoreFilePath = ".\\ignore.txt"
	botFilePath = ".\\botlist.txt"
	userList = []
	ignoreList = []
	botList = []
	
	#Auto Start/End time (24-hr)
	startHour = 8
	stopHour = 17
	
	# Anti-spam
	lastHelp = ("", "")
	lastRules = ("", "")
	lastPoints = ("", "")

	def __init__(self):
		self.restore()

	"""
	Twisted IRC Client Methods
	"""

	# Called when bot joins the IRC network
	def signedOn(self):
		# Join the channel and grab any new names we don't have
		self.join(self.channel)
		self.sendLine("WHO {}".format(self.channel))
	
	# Called when a PM is sent to the bot or to a channnel on the network
	# We use this to add someone to the game whenever they first send a message
	#  as well as handle admin/user commands and point exchanges.
	def privmsg(self, user, channel, message):
		# Accept admin PMs or messages on our channel
		if ((channel == self.channel) or (user.split('@')[1] == self.adminIP)):
			# In automatic mode, run the game during work hours and refresh gift points in the morning
			if self.autoMode:
				hour = int(self.getCurrentTime()[0])
				if (hour >= self.startHour and hour < self.stopHour):
					if not self.gameRunning:
						self.resetGame()
				elif self.gameRunning:
					self.stopGame()
					self.save()
			print ("{}: {}".format(user, message))
			nick = user.split('!')[0]
			ip = user.split('@')[1]
			if nick in self.botList:
				return
			if (message.startswith(self.nickname + ", ")):
				if (ip == self.adminIP):
					self.adminCommands(message.split(", ")[1])
				else:
					self.userCommands(nick, message.split(", ")[1])
			elif (message.startswith('+') or message.startswith('-')):
				self.pointMessage(nick, message)
		else:
			print user
		return
	
	# Called when a user joins the channel. Currently used for auto-kick when testing + polling new users
	def userJoined(self, user, channel):
		if (user != self.adminNick and self.testing):
			self.kick(channel, user, reason="I'm testing, please do not disturb :^)")
		else:
			self.sendLine("WHO {}".format(user))
		return
	
	# Called when a user changes their nick. Updates their user list entry.
	def userRenamed(self, oldname, newname):
		index = self.getUserIndex(oldname)
		if (index != -1):
			self.userList[index].nick = newname
		return
	
	# Calls the /who command to get a list of users; used when we restore to grab everyone in the channel
	def irc_RPL_WHOREPLY(self, prefix, params):
		ip = params[3]
		nick = params[5]
		if (nick not in self.botList) and (ip not in self.ignoreList):
			for user in self.userList:
				# Account for nick updates since last check
				if (ip == user.ip):
					user.nick = nick
					return
			self.userList.append(player(nick, ip))
		return
		
	"""
	Command Lists
	"""
	def adminCommands(self, message):
		if (message == "start"):
			self.autoMode = False
			self.gameRunning = True
			print("The point game has been started")
		elif (message == "stop"):
			self.autoMode = False
			self.gameRunning = False
			print("The point game has been stopped")
		elif (message == "auto"):
			self.autoMode = True
			print("The point game is now in auto mode")
		elif (message == "reset"):
			self.resetGame()
		elif (message == "save"):
			self.save()
		elif (message == "restore"):
			self.restore()
		elif (message.startswith("say ")):
			self.msg(self.channel, message.split("say ")[1])
		elif (message.startswith("setpts ")):
			setMsg = message.split(" ")
			self.setUserPoints(setMsg[1], setMsg[2])
		elif (message.startswith("setgp ")):
			setMsg = message.split(" ")
			self.setUserGP(setMsg[1], setMsg[2])
		elif (message.startswith("del ")):
			self.delUser(message.split(" ")[1])
		elif (message.startswith("ignore ")):
			self.ignoreUser(message.split(" ")[1])
		elif (message.startswith("unignore ")):
			self.unignoreUser(message.split(" ")[1])
		else:
			self.userCommands(self.adminNick, message)
		return
		
	def userCommands(self, nick, message):
		if (message == "help"):
			if self.getCurrentTime() != self.lastHelp:
				print("Admin Commands: start, stop, auto, reset, save, restore, say <msg>, setpts <user/all> <points>, setgp <user/all> <gp>, del <user>, ignore <user>, unignore <user>")
				self.msg(self.channel, "User Commands: help, rules, points, unsub [e.g. pointBot, help]")
				self.msg(self.channel, "Point Exchanges: +/-<pts> to <user> [reason] (e.g. +1 to pointBot for being awesome)")
				self.lastHelp = self.getCurrentTime()
		elif (message == "rules"):
			if self.getCurrentTime() != self.lastRules:
				self.msg(self.channel, "Hello, it's me, pointBot. I keep track of +s and -s handed out in the IRC. " +
					 "You get 10 points to give away every day, and these points are refreshed every morning at 8 AM. " +
					 "Using bots is not allowed. If you run into any issues, talk to the admin (J. Long). " +
					 "Have a day.")
				self.lastRules = self.getCurrentTime()
		elif (message == "points"):
			if self.getCurrentTime() != self.lastPoints:
				self.displayPoints()
				self.lastPoints = self.getCurrentTime()
		elif (message == "unsub"):
			self.ignoreUser(nick)
		elif (message.startswith('+') or message.startswith('-')):
			self.pointMessage(nick, message)
		return
		
	"""
	Command Functions
	"""
	# (Admin command) Resets gift points and starts the game; called at the beginning of every day and on startup
	def resetGame(self):
		self.gameRunning = True
		for user in self.userList:
			user.giftPoints = 10
		self.msg(self.channel, "The game has been reset. Gift points have been restored.")
		return
		
	# (Admin command) Saves user points and ignore list to files; called at the end of every day
	def save(self):
		pointsFile = open(self.pointsFilePath, 'w')
		for user in self.userList:
			pointsFile.write("{}:{}:{}:{}\n".format(user.nick, user.ip, user.totalPoints, user.giftPoints))
		pointsFile.close()
		print("Points saved.")
		
		ignoreFile = open(self.ignoreFilePath, 'w')
		for ignore in self.ignoreList:
			ignoreFile.write(ignore + "\n")
		ignoreFile.close()
		print("Ignore list saved.")
		return
		
	# (Admin command) Restores user/points list, ignore list, and bot list from files; called on startup or from admin command
	def restore(self):
		try:
			self.userList = []
			pointsFile = open(self.pointsFilePath, 'r')
			users = pointsFile.readlines()
			for user in users:
				userString = user.split(':')
				self.userList.append(player(userString[0], userString[1]))
				self.userList[-1].totalPoints = int(userString[2])
				self.userList[-1].giftPoints = int(userString[3].rstrip())
			pointsFile.close()
			print("Points restored.")
		except Exception, e:
			print("Restore failed: " + str(e))
			exit("Points restore fail")
		
		try:
			self.ignoreList = []
			ignoreFile = open(self.ignoreFilePath, 'r')
			ignored = ignoreFile.readlines()
			for ignore in ignored:
				self.ignoreList.append(ignore.split('\n')[0])
			ignoreFile.close()
			print("Ignore file restored.")
		except Exception, e:
			print("Restore failed: " + str(e))
			exit("Ignore restore fail")

		try:
			self.botList = []
			botFile = open(self.botFilePath, 'r')
			bots = botFile.readlines()
			for bot in bots:
				self.botList.append(bot.split('\n')[0])
			botFile.close()
			print("Bot file restored.")
		except Exception, e:
			print("Restore failed: " + str(e))
			exit("Bot restore fail")
		return
	
	# (Admin command) Sets a user's points
	def setUserPoints(self, nick, points):
		if nick == "all":
			for user in self.userList:
				user.totalPoints = int(points);
			print("all user points set to " + points)
		else:
			index = self.getUserIndex(nick)
			if (index == -1):
				print("Invalid username.")
				return
			self.userList[index].totalPoints = int(points)
			print(nick + " points set to " + points)
		return
		
	# (Admin command) Sets a user's gift points
	def setUserGP(self, nick, gp):
		if nick == "all":
			for user in self.userList:
				user.giftPoints = int(gp);
			print("all user gift points set to " + gp)
		else:
			index = self.getUserIndex(nick)
			if (index == -1):
				print("Invalid username.")
				return
			self.userList[index].giftPoints = int(gp)
			print(nick + " gift points set to " + gp)
		return
	
	# (Admin command) Removes a user from the points list
	def delUser(self, nick):
		index = self.getUserIndex(nick)
		if (index == -1):
			print("Invalid username.")
			return
		del self.userList[index]
		return
	
	# (Admin/user command) Ignores a user (pointBot ignores all messages from this user, ignores point exchanges, hides from points display if they are past player)
	def ignoreUser(self, nick):
		index = self.getUserIndex(nick)
		if (index == -1):
			print("Invalid username.")
			return
			
		if self.userList[index].ip not in self.ignoreList:
			self.ignoreList.append(self.userList[index].ip)
			print(nick + " ignored")
		return
	
	# (Admin command) Unignores a user
	def unignoreUser(self, nick):
		index = self.getUserIndex(nick)
		if (index == -1):
			print("Invalid username.")
			return
			
		if self.userList[index].ip in self.ignoreList:
			self.ignoreList.remove(self.userList[index].ip)
			print(nick + " unignored")
		return
	
	# (User command) Displays points
	def displayPoints(self):
		self.msg(self.channel, "Here is a list of points in the format \'User: Points\'")
		self.sortUserList()
		pointsList = ""
		for user in self.userList:
			if user.ip not in self.ignoreList:
				if user != self.userList[-1]:
					pointsList += "{}: {}, ".format(user.nick, user.totalPoints)
				else:
					pointsList += "{}: {}".format(user.nick, user.totalPoints)
		self.msg(self.channel, pointsList)
		return
		
	# (User command) Exchanges points between two players
	def pointMessage(self, sender, message):
		# Message format: +/-<pts> to <user> [reason]
		validMsg = match('^(\+|-)(\d+)\s(to\s)?(\w+).*$', message)
		if validMsg is not None:
			senderIndex = self.getUserIndex(sender)
			if not self.gameRunning:
				self.msg(sender, "The point game is not running at the moment.")
				return
			if self.userList[senderIndex].ip in self.ignoreList:
				self.msg(sender, "You've been ignored. If this was a mistake, take it up with the admin.")
				return
			
			sign = validMsg.group(1)
			number = validMsg.group(2)
			target = validMsg.group(4)
			
			# No self-points, and can't send more gift points than you currently have, can't send 0 points
			if int(number) == 0:
				self.msg(sender, "Nice try, dingus")
				return
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
				self.userList[targetIndex].totalPoints += int(number)
			else:
				self.userList[targetIndex].totalPoints -= int(number)
			self.userList[senderIndex].giftPoints -= int(number)
			
			if self.userList[senderIndex].giftPoints <= 0:
				self.msg(self.channel, sender + " has just run out of gift points for the day.")
			
			self.msg(sender, "You have gifted " + sign + number + " points to " + target + ". You have " + str(self.userList[senderIndex].giftPoints) + " gift points left for the day.")
		return
		
	"""
	Utility Functions
	"""
	# Gets index of user in user list based on nick
	def getUserIndex(self, nick):
		for i, user in enumerate(self.userList):
			if (user.nick == nick):
				return i
		return -1
	
	# Sorts user list in descending order based on number of points
	def sortUserList(self):
		self.userList = sorted(self.userList, key=lambda player: player.totalPoints, reverse=True)
			
	# Gets time of day; used for auto-start/stop and anti-spam
	@staticmethod
	def getCurrentTime():
		time = match('^(\d+):(\d+)', str(datetime.now().time()))
		return time.group(1), time.group(2)