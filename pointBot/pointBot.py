'''
--------------------------------------------------------------------------------------------------------------------
 Author: jlong
 Date: January 2018
 Description: This connects to an IRC channel and keeps track of arbitrary points given out by other users.
--------------------------------------------------------------------------------------------------------------------
'''
from twisted.words.protocols import irc
from datetime import datetime
from time import time
from re import match
from shutil import copyfile
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
	adminIP = "172.22.116.14"
	
	# Game state
	testing = False
	gameRunning = False
	autoMode = False
	
	# Restore file/user info
	pointsFilePath = ".\\points.txt"
	ignoreFilePath = ".\\ignore.txt"
	botFilePath = ".\\botlist.txt"
	archivePath = ".\\archive\\"
	userList = []
	ignoreList = []
	botList = []
	
	#Auto Start/End time (24-hr)
	startHour = 8
	stopHour = 17
	
	# Anti-spam
	lastHelp = 0
	lastRules = 0
	lastPoints = 0

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
		nick = user.split('!')[0]
		ip = user.split('@')[1]
		print ("{}: {} @ {}".format(user, message, channel))
		if nick in self.botList:
			return
		# Accept admin PMs, messages on our channel, or status requests
		if (message.startswith("{}, status ".format(self.nickname))):
			self.statusUser(nick, message.split("status ")[1])
		elif ((channel == self.channel) or (user.split('@')[1] == self.adminIP)):
			# In automatic mode, run the game during work hours and refresh gift points in the morning
			if self.autoMode:
				hour = int(self.getCurrentTime()[0])
				if (hour >= self.startHour and hour < self.stopHour):
					if not self.gameRunning:
						self.resetGame()
				elif self.gameRunning:
					self.stopGame()
					self.save()
					self.archive()
			if (message.startswith("{}, ".format(self.nickname))):
				if (ip == self.adminIP):
					self.adminCommands(message.split(", ")[1])
				else:
					self.userCommands(nick, message.split(", ")[1])
			elif (message.startswith('+') or message.startswith('-')):
				self.pointMessage(nick, message)
		return
	
	# Called when a user joins the channel. Currently used for auto-kick when testing + polling new users
	def userJoined(self, user, channel):
		index = self.getUserIndex(user)
		if (self.userList[index].ip != self.adminIP and self.testing):
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
	
	# Calls the /who command to get a list of users; used when we join/a new user joins the channel
	def irc_RPL_WHOREPLY(self, prefix, params):
		ip = params[3]
		nick = params[5]
		if (nick not in self.botList):
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
		elif (message.startswith("me ")):
			self.describe(self.channel, message.split("me ")[1])
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
			for user in self.userList:
				if user.ip == self.adminIP:
					self.userCommands(user.nick, message)
					return
			print("Error finding admin nick")
		return
		
	def userCommands(self, nick, message):
		if (message == "help"):
			if (time() - self.lastHelp) > 60:
				print("Admin Commands: start, stop, auto, reset, save, restore, say <msg>, setpts <user/all> <points>, setgp <user/all> <gp>, del <user>, ignore <user>, unignore <user>")
				self.msg(self.channel, "User Commands: help, rules, points, unsub, status <nick> (PM only) [e.g. pointBot, help]")
				self.msg(self.channel, "Point Exchanges: +/-<pts> [to] <user> [reason] (e.g. +1 to user for being awesome)")
				self.lastHelp = time()
		elif (message == "rules"):
			if (time() - self.lastRules) > 60:
				self.msg(self.channel, "Hello, it's me, pointBot. I keep track of +s and -s handed out in the IRC. " +
					 "You get 10 points to give away every day, and these points are refreshed every morning at 8 AM. " +
					 "Using bots is not allowed. If you run into any issues, talk to the admin (J. Long). " +
					 "Have a day.")
				self.lastRules = time()
		elif (message == "points"):
			if (time() - self.lastPoints) > 60:
				self.displayPoints()
				self.lastPoints = time()
		elif (message == "unsub"):
			self.ignoreUser(nick)
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
			pointsFile.write("{}:{}:{}:{}\n".format(user.nick, user.ip, user.giftPoints, user.totalPoints))
		pointsFile.close()
		print("Points saved.")
		
		ignoreFile = open(self.ignoreFilePath, 'w')
		for ignore in self.ignoreList:
			ignoreFile.write("{}\n".format(ignore))
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
				self.userList[-1].giftPoints = int(userString[2])
				self.userList[-1].totalPoints = int(userString[3].rstrip())
			pointsFile.close()
			print("Points restored.")
		except Exception, e:
			print("Restore failed: {}".format(str(e)))
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
			print("Restore failed: ".format(str(e)))
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
			print("Restore failed: ".format(str(e)))
			exit("Bot restore fail")
		return
	
	# (Admin command) Sets a user's points
	def setUserPoints(self, nick, points):
		if nick == "all":
			for user in self.userList:
				user.totalPoints = int(points);
			print("all user points set to {}".format(points))
		else:
			index = self.getUserIndex(nick)
			if (index == -1):
				print("Invalid username.")
				return
			self.userList[index].totalPoints = int(points)
			print("{} points set to {}".format(nick, points))
		return
		
	# (Admin command) Sets a user's gift points
	def setUserGP(self, nick, gp):
		if nick == "all":
			for user in self.userList:
				user.giftPoints = int(gp);
			print("all user gift points set to {}".format(gp))
		else:
			index = self.getUserIndex(nick)
			if (index == -1):
				print("Invalid username.")
				return
			self.userList[index].giftPoints = int(gp)
			print("{} gift points set to {}".format(nick, gp))
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
			print("{} ignored".format(nick))
		return
	
	# (Admin command) Unignores a user
	def unignoreUser(self, nick):
		index = self.getUserIndex(nick)
		if (index == -1):
			print("Invalid username.")
			return
			
		if self.userList[index].ip in self.ignoreList:
			self.ignoreList.remove(self.userList[index].ip)
			print("{} unignored".format(nick))
		return
	
	# (User command) Displays points
	def displayPoints(self):
		self.msg(self.channel, "Here is a list of points in the format \'User: Points\'")
		self.sortUserList()
		pointsList = ""
		for user in self.userList:
			if user.ip not in self.ignoreList:
				if user != self.userList[-1]:
					pointsList += "_{}_: {}, ".format(user.nick, user.totalPoints)
				else:
					pointsList += "_{}_: {}".format(user.nick, user.totalPoints)
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
			targetIndex = self.getUserIndex(target)
			
			# No self-points, can't send more gift points than you currently have, can't send 0 points, can't send to unknown/ignored user
			if int(number) == 0:
				self.msg(sender, "Nice try, dingus")
				return
			if self.userList[senderIndex].nick == target:
				self.msg(sender, "Nice try, dingus")
				return
			if (targetIndex == -1) or (self.userList[targetIndex].nick in self.ignoreList):
				self.msg(sender, "User {} is not in the game. No points exchanged.".format(target))
				return
			if self.userList[senderIndex].giftPoints <= 0:
				self.msg(sender, "You are out of gift points for the day! No points exchanged.")
				return
			if self.userList[senderIndex].giftPoints < int(number):
				self.msg(sender, "You only have {} gift points remaining! No points exchanged.".format(str(self.userList[senderIndex].giftPoints)))
				return
				
			if sign == '+':
				self.userList[targetIndex].totalPoints += int(number)
			else:
				self.userList[targetIndex].totalPoints -= int(number)
			self.userList[senderIndex].giftPoints -= int(number)
			
			if self.userList[senderIndex].giftPoints <= 0:
				self.msg(self.channel, "{} has just run out of gift points for the day.".format(sender))
			
			self.msg(sender, "You have gifted {}{} points to {}. You have {} gift points left for the day.".format(sign, number, target, str(self.userList[senderIndex].giftPoints)))
		return
		
	# (User command) Returns status of player via PM
	def statusUser(self, sender, target):
		index = self.getUserIndex(target)
		if (index == -1):
			self.msg(sender, "{} is not in the game.".format(target))
			return
		self.msg(sender, "{} status:\nGift points: {}\nTotal points: {}".format(target, self.userList[index].giftPoints, self.userList[index].totalPoints))
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
		
	# Used to archive the points file at the end of the day for backup purposes
	def archive(self):
		date = str(datetime.now()).split(' ')[0]
		copyfile(self.pointsFile, "{}{}.txt".format(self.archivePath, date))
		print("Points archived.")
		return