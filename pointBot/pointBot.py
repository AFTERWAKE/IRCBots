'''
--------------------------------------------------------------------------------------------------------------------
 Author: jlong
 Date: January 2018
 Description: This connects to an IRC channel and keeps track of arbitrary points given out by other users.
--------------------------------------------------------------------------------------------------------------------
'''
from twisted.internet import reactor, protocol
from twisted.words.protocols import irc
from datetime import datetime
from time import time
from re import compile, match
from shutil import copyfile
from sys import exit

class player:
	totalPoints = 0
	giftPoints = 10
	nick = ""
	ip = ""
	lastPM = 0

	def __init__(self, nick, ip):
		self.nick = nick
		self.ip = ip
		
class pointBot(irc.IRCClient):
	# IRC info
	nickname = "pointBot"
	channel = "#main"
	adminIP = "172.22.116.14"
	
	# Game state
	gameRunning = False
	autoMode = False
	testKey = "beepboop"		# Used when want to test in a keyword-protected channel
	
	# Restore file/user info
	pointsFilePath = ".\\restore\\points.txt"
	ignoreFilePath = ".\\restore\\ignore.txt"
	botFilePath = ".\\restore\\botlist.txt"
	userList = []
	ignoreList = []
	botList = []
	
	#Auto Start/End time, save times (24-hr)
	startHour = 8
	stopHour = 17
	lastSaveHour = 0
	
	# Anti-spam
	lastHelp = 0
	lastRules = 0
	lastPoints = 0
	
	# Compiled regex
	cmdExpr = compile("^([a-zA-Z]+)(?:\s(\w+)(?:\s(\d+))?)?$")
	ptExpr = compile("^(\+|-)(\d+)\s(?:to\s)?(\w+).*$")
	timeExpr = compile("^(\d+):(\d+):(\d+)")

	def __init__(self):
		self.restore()

	"""
	Twisted IRC Client Methods
	"""

	# Called when bot joins the IRC network
	def signedOn(self):
		# Join the channel and grab any new names we don't have
		self.join(self.channel, key=self.testKey)
		self.sendLine("WHO {}".format(self.channel))
	
	# Called when a PM is sent to the bot or to a channnel on the network
	# We use this to add someone to the game whenever they first send a message
	#  as well as handle admin/user commands and point exchanges.
	def privmsg(self, user, channel, message):
		nick = user.split('!')[0]
		ip = user.split('@')[1]
		hour, minute, second = self.getCurrentTime()
		print ("[{:02d}:{:02d}:{:02d}] {}: {} @ {}".format(hour, minute, second, user, message, channel))
		if nick in self.botList:
			return
		# In automatic mode, save every hour, run the game during work hours, and refresh gift points in the morning	
		if self.autoMode:
			if hour != self.lastSaveHour:
				self.save()
				self.lastSaveHour = hour
			if (hour >= self.startHour and hour < self.stopHour):
				if not self.gameRunning:
					self.resetGame()
			elif self.gameRunning:
				self.gameRunning = False
				self.save()
		# Treat every non-admin PM as status request, rate-limit
		if (channel == self.nickname and ip != self.adminIP):
			index = self.getUserIndex(nick)
			if (time() - self.userList[index].lastPM) > 10:
				self.statusUser(nick, nick)
				self.userList[index].lastPM = time()
		# Accept commands from active channel or admin PMs
		elif ((channel == self.channel) or (ip == self.adminIP)):
			# Check for command pattern (pointBot, <cmd>)
			if message.startswith(self.nickname + ", "):
				if (ip == self.adminIP):
					self.adminCommands(nick, message.split(self.nickname + ", ")[1])
				else:
					self.userCommands(nick, message.split(self.nickname + ", ")[1])
				return
			
			# Check for point exchange pattern (+1 [to] <user> [reason])
			if message.startswith("+") or message.startswith("-"):
				pointMatch = self.ptExpr.match(message)
				if pointMatch:
					self.pointMessage(nick, pointMatch.group(1), pointMatch.group(2), pointMatch.group(3))
		return
	
	# Called when a user joins the channel. Currently used for auto-kick when testing + polling new users
	def userJoined(self, user, channel):
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
	def adminCommands(self, nick, message):
		# Split the command into the common arguments
		cmdMatch = self.cmdExpr.match(message)
		if not cmdMatch:
			return
		else:
			command = cmdMatch.group(1)
			target = cmdMatch.group(2)
			value = cmdMatch.group(3)
			
		if command == "start":
			self.autoMode = False
			self.gameRunning = True
			print("The point game has been started")
		elif command == "stop":
			self.autoMode = False
			self.gameRunning = False
			print("The point game has been stopped")
		elif command == "auto":
			self.autoMode = True
			print("The point game is now in auto mode")
		elif command == "reset":
			self.resetGame()
		elif command == "save":
			self.save()
		elif command == "restore":
			self.restore()
		elif command == "say":
			self.msg(self.channel, message.split(" ")[1])
		elif command == "me":
			self.describe(self.channel, message.split(" ")[1])
		elif command == "status" and target:
			self.statusUser(nick, target)
		elif command == "setpts" and target and value:
			self.setUserPoints(target, value)
		elif command == "setgp" and target and value:
			self.setUserGP(target, value)
		elif command == "ignore" and target:
			self.ignoreUser(target)
		elif command == "unignore" and target:
			self.unignoreUser(target)
		else:
			self.userCommands(nick, message)
		return
		
	def userCommands(self, nick, message):
		if message == "help":
			if (time() - self.lastHelp) > 20:
				print("Admin Commands: start, stop, auto, reset, save, restore, say <msg>, me <action>, status <user>, setpts <user/all> <points>, setgp <user/all> <gp>, ignore <user>, unignore <user>")
				self.msg(self.channel, "User Commands: help, rules, points, unsub, [e.g. pointBot, help]. PM anything for your status.")
				self.msg(self.channel, "Point Exchanges: +/-<pts> [to] <user> [reason] (e.g. +1 to user for being awesome)")
				self.lastHelp = time()
		elif message == "rules":
			if (time() - self.lastRules) > 20:
				self.msg(self.channel, "Hello, it's me, pointBot. I keep track of +s and -s handed out in the IRC. " +
					 "You get 10 points to give away every day, and these points are refreshed every morning at 8 AM. " +
					 "Using bots is not allowed. If you run into any issues, talk to the admin (J. Long). " +
					 "Have a day.")
				self.lastRules = time()
		elif message == "points":
			if (time() - self.lastPoints) > 20:
				self.displayPoints()
				self.lastPoints = time()
		elif message == "unsub":
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
		print("Game reset.")
		return
		
	# (Admin command) Saves user points and ignore list to files; called at the end of every day
	def save(self):
		pointsFile = open(self.pointsFilePath, 'w')
		for user in self.userList:
			pointsFile.write("{}:{}:{}:{}\n".format(user.nick, user.ip, user.giftPoints, user.totalPoints))
		pointsFile.close()
		copyfile(self.pointsFilePath, ".\\points_copy.txt")
		print("Points saved.")
		
		ignoreFile = open(self.ignoreFilePath, 'w')
		for ignore in self.ignoreList:
			ignoreFile.write("{}\n".format(ignore))
		ignoreFile.close()
		copyfile(self.ignoreFilePath, ".\\ignore_copy.txt")
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
			print("Restore failed: {}".format(e))
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
			print("Restore failed: {}".format(e))
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
			print("Restore failed: {}".format(e))
			exit("Bot restore fail")
		return
		
	# (Admin command) Returns status of player via PM; also triggered by user PMs
	def statusUser(self, sender, target):
		index = self.getUserIndex(target)
		if (index == -1):
			self.msg(sender, "{} is not in the game.".format(target))
			return
		self.msg(sender, "{} status:\nGift points: {}\nTotal points: {}".format(target, self.userList[index].giftPoints, self.userList[index].totalPoints))
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
		self.msg(self.channel, "Here is a list of points in the format 'User: Total Points'")
		self.sortUserList()
		pointsList = ""
		for user in self.userList:
			if user.ip not in self.ignoreList:
				if user != self.userList[-1]:
					pointsList += "|{}|: {}, ".format(user.nick, user.totalPoints)
				else:
					pointsList += "|{}|: {}".format(user.nick, user.totalPoints)
		self.msg(self.channel, pointsList)
		return
		
	# (User command) Exchanges points between two players
	def pointMessage(self, sender, sign, number, target):		
		senderIndex = self.getUserIndex(sender)
		targetIndex = self.getUserIndex(target)
	
		# Make sure point game is running and the user is not ignored
		if not self.gameRunning:
			self.msg(sender, "The point game is not running at the moment.")
			return
		if self.userList[senderIndex].ip in self.ignoreList:
			self.msg(sender, "You've been ignored. If this was a mistake, take it up with the admin.")
			return	
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
			self.msg(sender, "You only have {} gift points remaining! No points exchanged.".format(self.userList[senderIndex].giftPoints))
			return
				
		if sign == '+':
			self.userList[targetIndex].totalPoints += int(number)
		else:
			self.userList[targetIndex].totalPoints -= int(number)
		self.userList[senderIndex].giftPoints -= int(number)
		
		if self.userList[senderIndex].giftPoints <= 0:
			self.msg(self.channel, "{} has just run out of gift points for the day.".format(sender))
		
		self.msg(sender, "You have gifted {}{} points to {}. You have {} gift points left for the day.".format(sign, number, target, self.userList[senderIndex].giftPoints))
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
		time = self.timeExpr.match(str(datetime.now().time()))
		return int(time.group(1)), int(time.group(2)), int(time.group(3))

def main():
    serv_ip = 'coop.test.adtran.com'
    serv_port = 6667

    f = protocol.ReconnectingClientFactory()
    f.protocol = pointBot

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()

if __name__ == '__main__':
	main()
