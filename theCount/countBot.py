'''
--------------------------------------------------------------------------------------------------------------------
      Author: DavidS
   v2 Author: noahsiano
        Date: April 2015
Last Updated: February 2018
        NOTE: Run in linux in order to get the dictionary to work.
 Description: This connects to an IRC chatroom and plays a counting game at the times 8:30,
              11:00, 1:30, and 4. The game can also be initiated by one or two hosts listed.
              A count of the winners is kept so that people can see how good they really are.
    Commands: ADMIN COMMANDS
                   botNick, set <userNick> <timesWon> (set timesWon for user on a reset)
                   botNick, del <userNick> (delete a user from the list/winnings table)
                   botNick, start (starts game)
                   botNick, save (saves list of winners || also gets saved at the end of every game)
                   botNick, stop (quits current game)
                   botNick, users (prints list of users to console)
                   botNick, restore (restores winners from save file || also restores automatically on run)
                   botNick, say <msg> (sends message to channel as the bot)
                   botNick, mute <user> (mutes a user by IP, they will be ignored for commands and will not be able to play the game)
                   botNick, unmute <user> (undoes the actions of the `mute` command)
                   botNick, whois <user> (Gives the IP address of a user on the server)
                   botNick, quit <msg>{optional} (the bot leaves the channel, with an optional quit message)
              USER COMMANDS
                   botNick, help (help message)
                   botNick, loser (LOSER: <user who called>)
                   botNick, losers (list of losers)
                   botNick, winners (shows list of winners)
                   botNick, rules (shows list of rules)
                   botNick, version (shows version + link to github)
--------------------------------------------------------------------------------------------------------------------
'''
from twisted.words.protocols import irc
from random import (
                    seed,
                    randrange,
                    choice,
                    randint
                    )
from datetime import datetime
from re import match
from sys import exit
import time


class countBot(irc.IRCClient):
    version = "2.5.3"
    latestCommits = "https://github.com/AFTERWAKE/IRCBots/commits/master/theCount"
    nickname = "theCount"
    chatroom = "#theCount"
    scoresFilePath = "./scores.txt"
    mutedFilePath = "./muted.txt"
    numberForGame = 17
    currentNumber = 0
    numberPlayLimit = 0
    hourOfLastGame = 0
    gameRunning = False
    nameList = []
    admin = ["172.22.117.48", "172.22.116.80"]
    letterWords = {}
    wordForGame = ''
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    numberForAlphabet = -1
    botList = [
        "~dad", "~mom",
        "~nodebot", "~Magic_Con",
        "~Seahorse", "~dootbot",
        "~pointbot", "botprotec",
        "QuipBot"
    ]
    mutedList = []
    lastWHOIS = ''
    muteMode = ''
    timeLastCommand = 0
    timestampBuffer = 0

    def __init__(self):
        currentHour = int(self.getCurrentTime().split(':')[0])
        currentMinute = int(self.getCurrentTime().split(':')[1])
        self.hourOfLastGame = currentHour
        if ((currentHour == 8) or (currentHour == 13)):
            if (currentMinute < 30):
                self.hourOfLastGame = self.hourOfLastGame - 1
        try:
            self.restoreUsersFromFile()
            print 'Winners restored'
        except:
            print 'Restore failed. No file found.'
        try:
            self.letterWords = {letter: [word.strip() for word in open('/usr/share/dict/words', 'r')
                                if word.capitalize().startswith(letter)] for letter in self.alphabet}
            print 'Dictionary loaded'
        except:
            print 'Dictionary failed to load!'
            print 'Make sure you\'re running this on Linux!'
            exit('Dictionary fail')
        try:
            self.restoreMutedUsersFromFile()
            print 'Muted Users Restored'
        except:
            print 'No Muted Users Found'

    def signedOn(self):
        self.join(self.chatroom)

    def isTooManyEntries(self, timesNameAppeared):
        return (timesNameAppeared >= self.numberPlayLimit)

    def resetGame(self):
        self.gameRunning = False
        self.resetUsers()
        self.timestampBuffer = 3
        print 'GAME RESET!'
        return

    def resetUsers(self):
        for i in range(len(self.nameList)):
            self.nameList[i].numbersAdded = 0
            self.nameList[i].isKicked = False
        return

    def playLimit(self):
        if self.            numberForGame < 6:
            self.numberPlayLimit = 3
        elif self.numberForGame < 8:
            self.numberPlayLimit = randrange(int(self.numberForGame/2), int(self.numberForGame/2)+3)
        else:
            self.numberPlayLimit = randrange(int(self.numberForGame/2)-1, int(self.numberForGame/2)+3)
        return

    def startGame(self):
        self.gameRunning = True
        seed(pow(self.numberForGame, randrange(0, 100)))
        self.numberForGame = randrange(1, 32)
        self.playLimit()
        self.wordForGame = self.chooseWordForGame()
        print 'Winning number: {} (kick on: {})'.format(self.numberForGame, self.numberPlayLimit)
        self.msg(self.chatroom, "COUNTBOT INITIATED. The counting game is beginning. " +
                 "Start with 1 {}.".format(self.wordForGame))
        self.currentNumber = 1
        return

    def chooseWordForGame(self):
        chooseLetter = self.handleAlphabetNumber()
        wordForGame = choice(self.letterWords[self.alphabet[chooseLetter]])
        try:
            wordForGame = wordForGame[0:wordForGame.index('\'')]
        except:
            pass
        return (wordForGame)

    def handleAlphabetNumber(self):
        self.numberForAlphabet += 1
        if (self.numberForAlphabet == 26):
            self.numberForAlphabet = 0
        return (self.numberForAlphabet)

    def declareWinner(self, userIndex, name):
        self.msg(self.chatroom, '{} is the winner with {} {}!'.format(name, self.numberForGame, self.wordForGame))
        self.msg(self.chatroom, "*ahahah*")
        self.nameList[userIndex].timesWon += 1
        return

    def incrementCount(self, name):
        self.msg(self.chatroom, name + " counted " + str(self.currentNumber) + ' ' + self.wordForGame + ', ahahah...')
        self.currentNumber += 1
        return

    def kickUser(self, userIndex, name):
        self.msg(self.chatroom, name + " has been eliminated from the game. " +
                 "Too many numbers submitted. " + '{} {} is what we\'re on.'
                 .format(self.currentNumber, self.wordForGame))
        self.nameList[userIndex].isKicked = True
        return

    def kickUserNickChange(self, userIndex, name):
        self.msg(self.chatroom, name + " has been eliminated from the game. " +
                 "No changing your nickname! " + '{} {} is what we\'re on.'
                 .format(self.currentNumber, self.wordForGame))
        self.nameList[userIndex].isKicked = True
        return

    def alreadyKickedMessage(self, name):
        self.msg(self.chatroom, name + " has already been kicked. " +
                 '{} {} is what we\'re on.'.format(self.currentNumber, self.wordForGame))
        return

    def automateStart(self):
        if (self.gameRunning == False):
            hour = int(self.getCurrentTime().split(':')[0])
            minute = int(self.getCurrentTime().split(':')[1])
            if ((hour != self.hourOfLastGame) and (hour > 7 and hour < 17)):
                if (((hour == 8) and (minute >= 30)) or ((hour == 11) and (minute >= 0)) or
                ((hour == 13) and (minute >= 30)) or ((hour == 16) and (minute >= 0))):
                    self.hourOfLastGame = hour
                    self.resetGame()
                    self.startGame()

    def getWinningUser(self):
        topUser = player("")
        firstLoop = True;
        for user in range(len(self.nameList)):
            if (self.nameList[user].timesWon > 0):
                if (firstLoop):
                    topUser = self.nameList[user]
                    firstLoop = False
                elif (self.nameList[user].timesWon > topUser.timesWon):
                    topUser = self.nameList[user]
        return topUser

    def adminCommands(self, message):
        if ((message == self.nickname + ', stop') or (message == self.nickname + ': stop')  or (message == self.nickname + ' stop')):
            self.resetGame()
            self.msg(self.chatroom, "The counting game has been quit.")
        elif ((message == self.nickname + ", start") or (message == self.nickname + ": start") or (message == self.nickname + ' start')):
            self.resetGame()
            self.startGame()
        elif ((message.startswith(self.nickname + ', set')) or (message.startswith(self.nickname + ': set'))):
            try:
                self.setUserTimesWon(message)
            except:
                return
        elif ((message.startswith(self.nickname + ', del')) or (message.startswith(self.nickname + ': del'))):
            try:
                self.delUserFromList(message)
            except:
                return
        elif ((message == self.nickname + ', users') or (message == self.nickname + ': users') or (message == self.nickname + ' users')):
            self.printAllUsers()
        elif ((message == self.nickname + ', restore') or (message == self.nickname + ': restore') or (message == self.nickname + ' restore')):
            self.restoreUsersFromFile()
            print 'Scores restored'
        elif ((message == self.nickname + ', save') or (message == self.nickname + ': save') or (message == self.nickname + ' save')):
            self.saveScores()
            print 'Scores saved'
        elif ((message.startswith(self.nickname + ', say')) or (message.startswith(self.nickname + ': say'))):
            self.msg(self.chatroom, message[len(self.nickname)+6:])
        elif (message.startswith(self.nickname + ' say')):
            self.msg(self.chatroom, message[len(self.nickname)+5:])
        elif ((message.startswith(self.nickname + ', me')) or (message.startswith(self.nickname + ': me'))):
            self.describe(self.chatroom, message[len(self.nickname)+5:])
        elif (message.startswith(self.nickname + ' me')):
            self.describe(self.chatroom, message[len(self.nickname)+4:])
        elif (message.startswith(self.nickname + ', quit')):
            if (message[len(self.nickname)+7:]):
                self.quit(message[len(self.nickname)+7:])
            else:
                self.quit('*ah..ah..ah :\'( goodbye.')
        elif (message.startswith(self.nickname + ' quit')):
            if (message[len(self.nickname)+6:]):
                self.quit(message[len(self.nickname)+6:])
            else:
                self.quit('*ah..ah..ah :\'( goodbye.')
        elif (message.startswith(self.nickname + ', mute')):
            self.mute(message[len(self.nickname)+7:].split(" ")[0])
        elif (message.startswith(self.nickname + ' mute')):
            self.mute(message[len(self.nickname)+6:].split(" ")[0])
        elif (message.startswith(self.nickname + ', unmute')):
            self.unmute(message[len(self.nickname)+9:].split(" ")[0])
        elif (message.startswith(self.nickname + ' unmute')):
            self.unmute(message[len(self.nickname)+8:].split(" ")[0])
        elif (message.startswith(self.nickname + ', whois')):
            self._whois(message[len(self.nickname)+8:].split(" ")[0])
        else:
            self.userCommands('noahsiano', message)

    def delUserFromList(self, message):
        nameIndex = self.getUserIndex(message.split()[2])
        if (nameIndex != -1):
            del self.nameList[nameIndex]
        return

    def handleUser(self, name):
        nameIndex = self.getUserIndex(name)
        if (nameIndex == -1):
            nameIndex = self.createNewUser(name)
        return nameIndex

    def setUserTimesWon(self, message):
        nameIndex = self.handleUser(message.split()[2])
        self.nameList[nameIndex].timesWon = int(message.split()[3])
        print self.nameList[nameIndex].username + ' timesWon: ' + str(self.nameList[nameIndex].timesWon)
        return

    def printAllUsers(self):
        for user in range(len(self.nameList)):
            print '{}. {}: {}'.format(user,
                                      self.nameList[user].username,
                                      self.nameList[user].timesWon)
        return

    def playGame(self, name):
        nameIndex = self.handleUser(name)
        self.nameList[nameIndex].numbersAdded += 1

        if (self.nameList[nameIndex].isKicked):
            self.alreadyKickedMessage(name)
        else:
            if (self.isTooManyEntries(self.nameList[nameIndex].numbersAdded)):
                self.kickUser(nameIndex, name)
            else:
                if (self.currentNumber == self.numberForGame):
                    self.declareWinner(nameIndex, name)
                    self.resetGame()
                    self.sortUsersAscending()
                    self.saveScores()
                else:
                    self.incrementCount(name)
        return

    def displayWinners(self):
        self.msg(self.chatroom, 'Here is a list of winners in the format \'User: Times Won\'')
        self.msg(self.chatroom, self.getWinnerString())

    def displayWieners(self, name):
        self.msg(self.chatroom, 'Here is a list of wieners in the format \'User: Wiener Level\'')
        self.msg(self.chatroom, name + ': ' + str(randint(0, 100)))

    def getWinnerString(self):
        winnerString = ''
        firstLoop = True
        for user in range(len(self.nameList)):
            if (self.nameList[user].timesWon > 0):
                if (not firstLoop):
                    winnerString += ', '
                winnerString += '{}: {}'.format(self.nameList[user].username,
                                                self.nameList[user].timesWon)
                firstLoop = False
        return winnerString

    def getLoserString(self):
        loserString = ''
        firstLoop = True
        for user in range(len(self.nameList)):
            if (self.nameList[user].timesWon == 0):
                if (not firstLoop):
                    loserString += ', '
                loserString += '{}'.format(self.nameList[user].username)
                firstLoop = False
        return loserString

    def getAllUsers(self):
        users = ''
        firstLoop = True
        for user in range(len(self.nameList)):
            if (not firstLoop):
                users += '\n'
            users += '{}:{}'.format(self.nameList[user].username,
                                    self.nameList[user].timesWon)
            firstLoop = False
        return users

    def helpText(self):
        self.msg(self.chatroom, 'Hello co-ops of ADTRAN, I am countBot. My sole purpose is to spawn a quick ' +
                 'and fun counting game at 8:30, 11:00, 1:30, and 4. I can also be initialized by an admin, ' +
                 'noahsiano. If you have any problems with me, please defer to Noah. Have a nice day :) ' +
                 'Also... Bots are not allowed to play this game. Please don\'t ruin the fun.')
    def rulesText(self):
        self.msg(self.chatroom,
        '1- No bots. If a bot is found playing, they will be banned in the future from playing. ' +
        '2- No changing your nickname during the game. You will be kicked. ' +
        '3- No joining in on a second IRC client to play twice. Your score will be removed. ' +
        '4- If you\'re found abusing the bot commands in any way, your domain may accidentally end up whitelisted.')

    def displayVersion(self):
        self.msg(self.chatroom, "v{} - Latest: {}".format(self.version, self.latestCommits))

    def userCommands(self, name, message, isTopUser=False):
        if ((message == self.nickname + ', help') or (message == self.nickname + ': help') or (message == self.nickname + ' help')):
            self.helpText()
        elif ((message == self.nickname + ', version') or (message == self.nickname + ': version') or (message == self.nickname + ' version')):
            self.displayVersion()
        elif ((message == self.nickname + ', winners') or (message == self.nickname + ': winners') or (message == self.nickname + ' winners')):
            self.sortUsersAscending()
            self.displayWinners()
        elif ((message == self.nickname + ', wieners') or (message == self.nickname + ': wieners') or (message == self.nickname + ' wieners')):
            self.sortUsersAscending()
            self.displayWieners(name)
        elif ((message == self.nickname + ', loser') or (message == self.nickname + ': loser') or (message == self.nickname + ' loser')):
            self.showLoserMsg(name)
        elif ((message == self.nickname + ', losers') or (message == self.nickname + ': losers') or (message == self.nickname + ' losers')):
            self.displayLosers()
        elif ((message == self.nickname + ', top') or (message == self.nickname + ': top') or (message == self.nickname + ' top')):
            self.msg(self.chatroom, 'The current number 1 player is: ' + self.getWinningUser().username)
        elif ((message.startswith(self.nickname + ', say') or message.startswith(self.nickname + ': say')) and isTopUser):
            self.msg(self.chatroom, message[len(self.nickname)+6:])
        elif ((message == self.nickname + ', rules') or (message == self.nickname + ': rules') or (message == self.nickname + ' rules')):
            self.rulesText()

    def showLoserMsg(self, name):
        self.msg(self.chatroom, 'LOSER: {}'.format(name))

    def displayLosers(self):
        self.msg(self.chatroom, 'Here is a list of losers.')
        self.msg(self.chatroom, self.getLoserString())

    @staticmethod
    def getCurrentTime():
        time = match('^(\d+):(\d+)', str(datetime.now().time()))
        return (time.group(1) + ":" + time.group(2))

    def getUserIndex(self, name):
        for index in range(len(self.nameList)):
            if self.nameList[index].username == name:
                return (index)
        return (-1)

    def createNewUser(self, name):
        self.nameList.append(player(name))
        return (len(self.nameList) - 1)

    def sortUsersAscending(self):
        for i in range(len(self.nameList)):
            j = i
            while ((j > 0) and self.nameList[j - 1].timesWon < self.nameList[j].timesWon):
                self.swapPositions(j)
                j -= 1

    def swapPositions(self, index):
        temp = self.nameList[index]
        self.nameList[index] = self.nameList[index - 1]
        self.nameList[index - 1] = temp
        return

    def saveScores(self):
        saveFile = open(self.scoresFilePath, 'w')
        saveFile.write(self.getAllUsers())
        saveFile.close()
        return

    def saveMuted(self):
        saveFile = open(self.mutedFilePath, 'w')
        saveFile.write("\n".join(self.mutedList))

    def restoreUsersFromFile(self):
        returnFile = open(self.scoresFilePath, 'r')
        users = returnFile.readlines()
        returnFile.close()
        self.restoreScores(users)
        return

    def restoreScores(self, users):
        for user in users:
            user = user.split(':')
            index = self.handleUser(user[0])
            self.nameList[index].timesWon = int(user[1])

    def restoreMutedUsersFromFile(self):
        returnFile = open(self.mutedFilePath, 'r')
        users = returnFile.readlines()
        returnFile.close()
        self.restoreMuted(users)
        return

    def restoreMuted(self, users):
        for user in users:
            self.mutedList.append(user)

    def userRenamed(self, oldname, newname):
        if (self.gameRunning):
            nameIndex = self.handleUser(newname)
            if (self.nameList[nameIndex].isKicked):
                self.alreadyKickedMessage(newname)
            else:
                self.kickUserNickChange(nameIndex, newname)

    def isABot(self, name):
        self.msg(self.chatroom, name + ", you dirty bot, you... " +
                 '{} {} is what we\'re on.'.format(self.currentNumber, self.wordForGame))
        return

    def isMuted(self, name):
        self.msg(self.chatroom, name + ", someone told me not to trust you... " +
                 '{} {} is what we\'re on.'.format(self.currentNumber, self.wordForGame))
        return

    def mute(self, name):
        self.muteMode = 'mute'
        self.who(name)
        return

    def unmute(self, name):
        self.muteMode = 'unmute'
        self.who(name)
        return

    def _whois(self, name):
        self.muteMode = 'just a whois'
        self.who(name)

    def who(self, user):
        "Get the user's name, hostname, and IP Address"
        "usage: client.whois('testUser')"
        self.sendLine('WHOIS %s' % user)

    def irc_RPL_WHOISUSER(self, *nargs):
        "Receive WHOIS reply from server"
        "nargs in the format:"
        "(Server, [user-who-called-whois, username, hostname, IP, '*', realname])"
        ip = nargs[1][3]
        user = nargs[1][1]
        username = nargs[1][2].split("~")[1]
        print 'WHOIS:', ip
        self.lastWHOIS = ip
        if (self.muteMode == 'mute'):
            self.mute2(ip)
        elif (self.muteMode == 'unmute'):
            self.unmute2(ip)
        elif (self.muteMode == 'just a whois'):
            self.msg(self.chatroom, "%s's username is %s and their IP address is %s" % (user, username, ip))
        self.muteMode = ''

    def mute2(self, ip):
        self.msg(self.chatroom, "I seem to have lost a little bit of my hearing... It's probably nothing.")
        self.mutedList.append(ip)
        self.saveMuted()

    def unmute2(self, ip):
        try:
            self.mutedList.remove(ip)
            self.msg(self.chatroom, "Doc says my hearing is getting better!")
        except:
            self.msg(self.chatroom, "...really")
        self.saveMuted()

    def privmsg(self, user, channel, message):
        if ((channel == self.chatroom) or (user.split('@')[1] in self.admin)):
            try:
                if (self.gameRunning and int(message) != self.currentNumber):
                    print "{} -> {}: {}".format(str(time.time()), user, message)
                elif (not self.gameRunning and self.timestampBuffer > 0):
                    print "{} -> {}: {} LATE".format(str(time.time()), user, message)
                    self.timestampBuffer -= 1
                if (int(message) == self.currentNumber and self.gameRunning):
                    print "{} -> {}: {} COUNTED".format(str(time.time()), user, message)
                    hostname = user.split('!')[1].split('@')
                    if (hostname[0] in self.botList):
                        print("Bot!")
                        self.isABot(user.split('!')[0])
                        return
                    if (hostname[1] in self.mutedList):
                        print("Muted.")
                        self.isMuted(user.split('!')[0])
                        return
                    self.playGame(user.split('!')[0])
                else:
                    self.automateStart()
            except:
                self.automateStart()
                if (message.startswith(self.nickname)):
                    if (user.split('@')[1] in self.admin):
                        self.adminCommands(message)
                    elif (user.split('@')[1] in self.mutedList):
                        return
                    elif (user.split('!')[1] in self.botList):
                        return
                    elif (user.split('!')[0] == self.getWinningUser().username):
                        timeRightNow = time.time()
                        if (timeRightNow - self.timeLastCommand) > 5:
                            self.timeLastCommand = time.time()
                            self.userCommands(user.split('!')[0], message, True)
                    else:
                        timeRightNow = time.time()
                        if (timeRightNow - self.timeLastCommand) > 5:
                            self.timeLastCommand = time.time()
                            self.userCommands(user.split('!')[0], message)
        else:
            print user
        return


class player:
    numbersAdded = 0
    timesWon = 0
    username = ""
    isKicked = False

    def __init__(self, name):
        self.username = name
