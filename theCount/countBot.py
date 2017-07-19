'''
--------------------------------------------------------------------------------------------------------------------
      Author: DavidS
        Date: April 2015
        NOTE: Run in linux in order to get the dictionary to work.
 Description: This connects to an IRC chatroom and plays a counting game at the times 10,
              12, 2, and 4. The game can also be initiated by one or two hosts listed.
              A count of the winners is kept so that people can see how good they really are.
    Commands: ADMIN COMMANDS
                   botNick: set <userNick> <timesWon> (set timesWon for user on a reset)
                   botNick: del <userNick> (delete a user from the list/winnings table)
                   botNick: start (starts game)
                   botNick: save (saves list of winners || also gets saved at the end of every game)
                   botNick: quit (quits current game)
                   botNick: users (prints list of users to console)
                   botNick: restore (restores winners from save file || also restores automatically on run)
                   botNick: say <msg> (sends message to channel as the bot)
              USER COMMANDS
                   botNick: help (help message)
                   botNick: loser (LOSER: <user who called>)
                   botNick: losers (list of losers)
                   botNick: winners (shows list of winners)
--------------------------------------------------------------------------------------------------------------------
'''
from twisted.words.protocols import irc
from random import (
                    seed,
                    randrange,
                    choice
                    )
from datetime import datetime
from re import match
from sys import exit


class countBot(irc.IRCClient):
    nickname = "theCount"
    chatroom = "#main"
    scoresFilePath = "./scores.txt"
    numberForGame = 17
    currentNumber = 0
    numberPlayLimit = 0
    hourOfLastGame = 0
    gameRunning = False
    nameList = []
    admin = "nsiano8300w7.adtran.com"
    letterWords = {}
    wordForGame = ''
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    numberForAlphabet = -1

    def __init__(self):
        self.hourOfLastGame = int(self.getCurrentTime().split(':')[0])
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

    def signedOn(self):
        self.join(self.chatroom)

    def isTooManyEntries(self, timesNameAppeared):
        return (timesNameAppeared >= self.numberPlayLimit)

    def resetGame(self):
        self.gameRunning = False
        self.resetUsers()
        print 'GAME RESET!'
        return

    def resetUsers(self):
        for i in range(len(self.nameList)):
            self.nameList[i].numbersAdded = 0
            self.nameList[i].isKicked = False
        return

    def playLimit(self):
        if self.numberForGame < 6:
            self.numberPlayLimit = 3
        else:
            self.numberPlayLimit = randrange(int(self.numberForGame/2)-1, int(self.numberForGame/2)+3)
        return

    def startGame(self):
        self.gameRunning = True
        seed(pow(self.numberForGame, randrange(0, 100)))
        self.numberForGame = randrange(1, 32)
        self.playLimit()
        self.wordForGame = self.chooseWordForGame()
        print 'Winning number: {}'.format(self.numberForGame)
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

    def alreadyKickedMessage(self, name):
        self.msg(self.chatroom, name + " has already been kicked. " +
                 '{} {} is what we\'re on.'.format(self.currentNumber, self.wordForGame))
        return

    def automateStart(self):
        hour = int(self.getCurrentTime().split(':')[0])
        minute = int(self.getCurrentTime().split(':')[1])
        if ((hour != self.hourOfLastGame) and (hour > 7 and hour < 17)):
            if (((hour == 8) and (minute >= 30)) or ((hour == 11) and (minute >= 0)) or
            ((hour == 13) and (minute >= 30)) or ((hour == 16) and (minute >= 0))):
                self.hourOfLastGame = hour
                self.resetGame()
                self.startGame()

    def getWinningUser(self):
        topUser = ''
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
        if (message == self.nickname + ', quit'):
            self.resetGame()
            self.msg(self.chatroom, "The counting game has been quit.")
        elif (message == self.nickname + ", start"):
            self.resetGame()
            self.startGame()
        elif (message.startswith(self.nickname + ', set')):
            try:
                self.setUserTimesWon(message)
            except:
                return
        elif (message.startswith(self.nickname + ', del')):
            try:
                self.delUserFromList(message)
            except:
                return
        elif (message == self.nickname + ', users'):
            self.printAllUsers()
        elif (message == self.nickname + ', restore'):
            self.restoreUsersFromFile()
            print 'Scores restored'
        elif (message == self.nickname + ', save'):
            self.saveScores()
            print 'Scores saved'
        elif (message.startswith(self.nickname + ', say')):
            self.msg(self.chatroom, message[len(self.nickname)+6:])
        elif (message.startswith(self.nickname + ', me')):
            self.describe(self.chatroom, message[len(self.nickname)+5:])
        else:
            self.userCommands('Noah Siano', message)

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

    def userCommands(self, name, message, isTopUser=False):
        if (message == self.nickname + ', help'):
            self.helpText()
        elif (message == self.nickname + ', winners'):
            self.sortUsersAscending()
            self.displayWinners()
        elif (message == self.nickname + ', loser'):
            self.showLoserMsg(name)
        elif (message == self.nickname + ', losers'):
            self.displayLosers()
        elif (message == self.nickname + ', top'):
            self.msg(self.chatroom, 'The current number 1 player is: ' + self.getWinningUser().username)
        elif (message.startswith(self.nickname + ', say') and isTopUser):
            self.msg(self.chatroom, message[len(self.nickname)+6:])

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

    def privmsg(self, user, channel, message):
        if ((channel == self.chatroom) or (user.split('@')[1] == self.admin)):
            try:
                if (int(message) == self.currentNumber and self.gameRunning):
                    print "{}: {}".format(user, message)
                    self.playGame(user.split('!')[0])
                else:
                    self.automateStart()
            except:
                self.automateStart()
                if (message.startswith(self.nickname)):
                    if (user.split('@')[1] == self.admin):
                        self.adminCommands(message)
                    elif (user.split('!')[0] == self.getWinningUser().username):
                        self.userCommands(user.split('!')[0], message, True)
                    else:
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
