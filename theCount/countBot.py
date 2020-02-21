# -*- coding: utf-8 -*-
'''
--------------------------------------------------------------------------------------------------------------------
      Author: DavidS
   v2 Author: noahsiano
        Date: April 2015
Last Updated: August 2019
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
                   botNick, me <me> (sends a /me message to the channel as the bot)
                   botNick, mute <user> (mutes a user by IP, they will be ignored for commands and will not be able to play the game)
                   botNick, unmute <user> (undoes the actions of the `mute` command)
                   botNick, whois <user> (Gives the IP address of a user on the server)
                   botNick, mock <user> (Mocks the user and shows their current points)
                   botNick, pmock <user> (Everything the user says is mocked)
                   botNick, unpmock <user> (Undoes the pmock command)
                   botNick, whowho <user> (Prints a WHO: command for <user>)
                   botNick, quit <msg>{optional} (the bot leaves the channel, with an optional quit message)
              USER COMMANDS
                   botNick, help (help message)
                   botNick, loser (LOSER: <user who called>)
                   botNick, losers (list of losers)
                   botNick, winners (shows list of winners)
                   botNick, wieners (shows your wiener count for the day)
                   botNick, words (shows the words you won the counting game with)
                   botNick, rules (shows list of rules)
                   botNick, version (shows version + link to github)
--------------------------------------------------------------------------------------------------------------------
'''
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from random import (
                    choice,
                    randint
                    )
from datetime import datetime
from re import match
from sys import exit
import time
import ast

serv_ip = "10.4.163.34"
serv_port = 6667


class CountBot(irc.IRCClient):
    version = "2.16.1"
    latestCommits = "https://github.com/AFTERWAKE/IRCBots/commits/master/theCount"
    nickname = "theCount"
    chatroom = "#main"
    scoresFilePath = "./scores.txt"
    mutedFilePath = "./muted.txt"
    numberForGame = 17
    currentNumber = 0
    numberPlayLimit = 0
    hourOfLastGame = 0
    gameRunning = False
    nameList = []
    admin = ["localhost", "162.243.65.242"]
    adminNames = ["noahsiano", "groot"]
    letterWords = {}
    wordForGame = ''
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    numberForAlphabet = -1
    botList = [
        "dad", "mom",
        "nodebot", "Magic_Conch",
        "Seahorse", "MemeBot",
        "pointbot", "botprotec",
        "QuipBot", "burnBot",
        "niceBot", "Mr_HighFive"
    ]
    mutedList = []
    lastWHOIS = ''
    muteMode = ''
    timeLastCommand = 0
    timestampBuffer = 0
    currentDay = -1

    def __init__(self):
        current_hour = int(self.getCurrentTime().split(':')[0])
        current_minute = int(self.getCurrentTime().split(':')[1])
        self.hourOfLastGame = current_hour
        if current_hour == 8 or current_hour == 13:
            if current_minute < 30:
                self.hourOfLastGame = self.hourOfLastGame - 1
        try:
            self.restoreUsersFromFile()
            print('Winners restored')
        except:
            print('Restore failed.')
        try:
            self.letterWords = {letter: [word.strip() for word in open('/usr/share/dict/words', 'r')
                                if word.capitalize().startswith(letter)] for letter in self.alphabet}
            print('Dictionary loaded')
        except:
            print('Dictionary failed to load!')
            print('Make sure you\'re running this on Linux!')
            exit('Dictionary fail')
        try:
            self.restoreMutedUsersFromFile()
            print('Muted Users Restored')
        except:
            print('No Muted Users Found')

    def signedOn(self):
        self.join(self.chatroom)

    def isTooManyEntries(self, timesNameAppeared):
        return timesNameAppeared >= self.numberPlayLimit

    def resetGame(self):
        self.gameRunning = False
        self.resetUsers()
        self.timestampBuffer = 3
        print('GAME RESET!')
        return

    def resetWieners(self):
        print("Reset wieners")
        for i in range(len(self.nameList)):
            if (self.nameList[i].dayOfLastWiener != datetime.now().day):
                self.nameList[i].hasNewWieners = False
            else:
                self.nameList[i].hasNewWieners = True


    def resetUsers(self):
        for i in range(len(self.nameList)):
            self.nameList[i].numbersAdded = 0
            self.nameList[i].isKicked = False
        return

    def playLimit(self):
        if self.numberForGame < 6:
            self.numberPlayLimit = 5
        else:
            self.numberPlayLimit = randint(int(self.numberForGame/2) + 2, int(self.numberForGame/2) + 4)
        return

    def startGame(self):
        self.gameRunning = True
        self.numberForGame = randint(1, 31)
        # Let's reduce the number of times the winning number is < 6 or > 25
        if self.numberForGame < 6 or self.numberForGame > 25:
            self.numberForGame = randint(1, 31)
            if self.numberForGame < 3 or self.numberForGame > 29:
                self.numberForGame = randint(1, 31)
        # There we go... Should see a lot less games where 1, 2, 30, and 31 win
        self.playLimit()
        self.wordForGame = self.chooseWordForGame()
        print('Winning number: {} (kick on: {})'.format(self.numberForGame, self.numberPlayLimit))
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
        topUser = self.getWinningUser().username
        if name == topUser:
            self.msg(self.chatroom, '{} is the winner...AGAIN... with {} {}. Can\'t believe you all keep letting {} win!'.format(name, self.numberForGame, self.wordForGame, name))
            self.describe(self.chatroom, "*ahahah*'s mockingly")
        else:
            self.msg(self.chatroom, '{} is the winner with {} {}!'.format(name, self.numberForGame, self.wordForGame))
            self.msg(self.chatroom, "*ahahah*")
        self.nameList[userIndex].timesWon += 1
        self.nameList[userIndex].wordsWon.append(self.wordForGame)
        return

    def incrementCount(self, name):
        topUser = self.getWinningUser().username
        if name == topUser:
            mockMsg = self.mockMe(name + ' counted ' + str(self.currentNumber) + ' ' + self.wordForGame + ', ahahah...')
            self.msg(self.chatroom, mockMsg)
        else:
            self.msg(self.chatroom, name + " counted " + str(self.currentNumber) + ' ' + self.wordForGame + ', ahahah...')
        self.currentNumber += 1
        return

    def mockMe(self, msg):
        return "".join(choice([letter.upper(), letter]) for letter in msg)

    def mockUser(self, name):
        nameIndex = self.getUserIndex(name)
        if nameIndex != -1:
            points = self.nameList[nameIndex].timesWon
            if points == 1:
                self.msg(self.chatroom, self.mockMe("i am " + name + " and i have " + str(points) + " point"))
            else:
                self.msg(self.chatroom, self.mockMe("i am " + name + " and i have " + str(points) + " points"))

    def permaMockUser(self, name):
        nameIndex = self.getUserIndex(name)
        if nameIndex != -1:
            self.nameList[nameIndex].permaMock = True

    def unpermaMockUser(self, name):
        nameIndex = self.getUserIndex(name)
        if nameIndex != -1:
            self.nameList[nameIndex].permaMock = False

    def userPermaMocked(self, name):
        nameIndex = self.getUserIndex(name)
        if nameIndex != -1:
            return self.nameList[nameIndex].permaMock
        else:
            return False

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
            day = int(self.getCurrentTime().split(':')[2])
            if day < 5:
                if ((hour != self.hourOfLastGame) and (hour > 7 and hour < 17)):
                    if (((hour == 8) and (minute >= 30)) or ((hour == 11) and (minute >= 0)) or
                    ((hour == 13) and (minute >= 30)) or ((hour == 16) and (minute >= 0))):
                        self.hourOfLastGame = hour
                        self.resetGame()
                        self.startGame()

    def checkResetWieners(self):
        day = datetime.now().day
        if (day != self.currentDay):
            self.resetWieners()
            self.currentDay = day

    def getWinningUser(self):
        topUser = Player("")
        firstLoop = True;
        for user in range(len(self.nameList)):
            if (self.nameList[user].timesWon > 0):
                if (firstLoop):
                    topUser = self.nameList[user]
                    firstLoop = False
                elif (self.nameList[user].timesWon > topUser.timesWon):
                    topUser = self.nameList[user]
        return topUser

    def adminCommands(self, name, message):
        if message.startswith(self.nickname + ', ') or message.startswith(self.nickname + ': '):
            command = message[len(self.nickname) + 2:].strip()
        elif message.startswith(self.nickname + ' '):
            command = message[len(self.nickname) + 1:].strip()
        else:
            return

        if command.startswith('stop'):
            self.resetGame()
            self.msg(self.chatroom, "The counting game has been quit.")
        elif command.startswith('start'):
            self.resetGame()
            self.startGame()
        elif command.startswith('set'): 
            try:
                self.setUserTimesWon(message)
            except:
                return
        elif command.startswith('del'): 
            try:
                self.delUserFromList(message)
            except:
                return
        elif command.startswith('users'):
            self.printAllUsers()
        elif command.startswith('restore'):
            self.restoreUsersFromFile()
            print('Scores restored')
        elif command.startswith('save'):
            self.saveScores()
            print('Scores saved')
        elif command.startswith('say '):
            self.msg(self.chatroom, command.replace('say ', '', 1))
        elif command.startswith('me '):
            self.describe(self.chatroom, command.replace('me ', '', 1))
        elif command.startswith('quit'):
            if len(command) > len('quit '):
                self.quit(command.replace('quit ', '', 1))
            else:
                self.quit('*ah..ah..ah :\'( goodbye.')
        elif command.startswith('mute'):
            self.mute(message.split()[2])
        elif command.startswith('unmute'):
            self.unmute(message.split()[2])
        elif command.startswith('whois'):
            self._whois(message.split()[2])
        elif command.startswith('mock'):
            i = 0
            for n in message.split()[2:]:
                self.mockUser(n)
                if (i > 3):
                    break
                i += 1
        elif command.startswith('pmock'):
            self.permaMockUser(message.split()[2])
        elif command.startswith('unpmock'):
            self.unpermaMockUser(message.split()[2])
        elif command.startswith('whowho'):
            self.whowho(self.chatroom)
        else:
            self.userCommands(name, command, already_stripped=True)

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
        print(self.nameList[nameIndex].username + ' timesWon: ' + str(self.nameList[nameIndex].timesWon))
        return

    def printAllUsers(self):
        for user in range(len(self.nameList)):
            print('{}. {}: {}: {}'.format(user,
                                      self.nameList[user].username,
                                      self.nameList[user].timesWon,
                                      self.nameList[user].wienerLevel))
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

    def displayWinnersChart(self):
        self.msg(self.chatroom, 'Here is a chart of winners:')
        self.msg(self.chatroom, self.getWinnerChart())

    def displayWieners(self, name):
        wieners = randint(0, 100)
        nameIndex = self.handleUser(name)
        if (not self.nameList[nameIndex].hasNewWieners):
            self.nameList[nameIndex].wienerLevel = wieners
            self.nameList[nameIndex].hasNewWieners = True
            self.nameList[nameIndex].dayOfLastWiener = datetime.now().day
        self.msg(self.chatroom, 'Here is a list of wieners in the format \'User: Wiener Level\'')
        self.msg(self.chatroom, name + ': ' + str(self.nameList[nameIndex].wienerLevel) + self.exclPoints(self.nameList[nameIndex].wienerLevel))
        if self.nameList[nameIndex].wienerLevel == 69:
            self.msg(self.chatroom, 'Nice.')
        elif self.nameList[nameIndex].wienerLevel == 0:
            self.msg(self.chatroom, 'Oof.')
        self.saveScores()

    def exclPoints(self, wieners):
        excl = '!'
        if wieners == 69:
            excl += '!!!!!111!1!11!'
        elif wieners == 0:
            excl = '.'
        elif wieners > 80:
            excl += '!!!'
        elif wieners > 50:
            excl += '!'
        return excl

    def getWinnerString(self):
        winnerString = ''
        firstLoop = True
        for user in range(len(self.nameList)):
            if (self.nameList[user].timesWon > 0):
                if (not firstLoop):
                    winnerString += ', '
                winnerString += '[{}]: {}'.format(self.nameList[user].username,
                                                self.nameList[user].timesWon)
                firstLoop = False
        return winnerString

    def getWinnerChart(self):
        maxlen = 0
        for user in range(len(self.nameList)):
            if (len(self.nameList[user].username) > maxlen):
                maxlen = len(self.nameList[user].username)
        winnerString = ''
        maxWins = self.nameList[0].timesWon
        firstLoop = True
        for user in range(len(self.nameList)):
            if (self.nameList[user].timesWon > 0):
                if (not firstLoop):
                    winnerString += '\n'
                winnerString += self.nameList[user].username + ":"
                remlen = maxlen - len(self.nameList[user].username)
                for i in range(remlen + 1):
                    winnerString += " "
                for i in range(self.nameList[user].timesWon):
                    winnerString += '#'
                for i in range(maxWins - self.nameList[user].timesWon):
                    winnerString += '|'
                firstLoop = False
        return winnerString

    def getWienerString(self, name, level):
        wienerString = name + ': '
        for user in range(len(self.nameList)):
            if self.nameList[user].username == name:
                if(self.nameList[user].wienerLevel):
                    wienerString += self.nameList[user].wienerLevel

    def getLoserString(self):
        loserString = ''
        firstLoop = True
        for user in range(len(self.nameList)):
            if (self.nameList[user].timesWon <= 0):
                if (not firstLoop):
                    loserString += ', '
                loserString += '[{}]'.format(self.nameList[user].username)
                firstLoop = False
        return loserString

    def getAllUsers(self):
        users = ''
        firstLoop = True
        for user in range(len(self.nameList)):
            if (not firstLoop):
                users += '\n'
            users += '{}:{}:{}:{}:{}'.format(self.nameList[user].username,
                                       self.nameList[user].timesWon,
                                       str(self.nameList[user].wordsWon),
                                       self.nameList[user].wienerLevel,
                                       self.nameList[user].dayOfLastWiener)
            firstLoop = False
        return users

    def helpText(self):
        self.msg(self.chatroom, 'Hello co-ops of ADTRAN, I am countBot. My sole purpose is to spawn a quick ' +
                 'and fun counting game at 8:30, 11:00, 1:30, and 4. I can also be initialized by an admin: ' +
                 '{}. If you have any problems with me, please defer to Noah. Have a very nice day :) '.format(", ".join(self.adminNames)) +
                 'Also... Bots are not allowed to play this game. Please don\'t ruin the fun.')
    def rulesText(self):
        self.msg(self.chatroom,
        '1- No bots. If a bot is found playing, they will be banned in the future from playing. ' +
        '2- No changing your nickname during the game. You will be kicked. ' +
        '3- No joining in on a second IRC client to play twice. Your score will be removed. ' +
        '4- If you\'re found abusing the bot commands in any way, your domain may accidentally end up whitelisted.')

    def displayVersion(self):
        self.msg(self.chatroom, "v{} - Latest: {}".format(self.version, self.latestCommits))

    def userCommands(self, name, message, isTopUser=False, already_stripped=False):
        if not already_stripped:
            if message.startswith(self.nickname + ', ') or message.startswith(self.nickname + ': '):
                command = message[len(self.nickname) + 2:].strip()
            elif message.startswith(self.nickname + ' '):
                command = message[len(self.nickname) + 1:].strip()
            else:
                return
        else:
            command = message

        if command.startswith('help'):
            self.helpText()
        elif command.startswith('version'):
            self.displayVersion()
        elif command.startswith('winners'):
            self.sortUsersAscending()
            self.displayWinners()
        elif command.startswith('wieners'):
            self.sortUsersAscending()
            self.displayWieners(name)
        elif command.startswith('chart'):
            self.sortUsersAscending()
            self.displayWinnersChart()
        elif command.startswith('losers'):
            self.displayLosers()
        elif command.startswith('loser'):
            self.showLoserMsg(name)
        elif command.startswith('top'):
            self.msg(self.chatroom, self.mockMe('The current number 1 player is: ' + self.getWinningUser().username))
        elif command.startswith('say') and isTopUser:
            self.msg(self.chatroom, message[len(self.nickname)+6:])
        elif command.startswith('mock') and isTopUser:
            i = 0
            for n in message.split()[2:]:
                self.mockUser(n)
                if (i > 1):
                    break
                i += 1
        elif command.startswith('rules'):
            self.rulesText()
        elif command.startswith('words'):
            self.displayWinningWords(name)
        elif command.startswith('donate'):
            print(command)
            self.donateWieners(name, command)


    def donateWieners(self, name, command):
        donation = command.split()
        message = "Invalid donation syntax. Example: \"theCount, donate [wiener amount] [username]\""
        if(len(donation) >= 3):
            if(self.getUserIndex(name) == -1):
                self.msg(self.chatroom, message)
            else:
                try :
                    int(donation[1])
                except:
                    self.msg(self.chatroom, message)
                    return
                if (int(donation[1]) > 0 or int(donation[1]) < 101):
                    donor = self.handleUser(name)
                    recipient = self.handleUser(donation[2])
                    message = ""
                    donorWieners = self.nameList[donor].wienerLevel
                    recipientWieners = self.nameList[recipient].wienerLevel
                    allowance = 100 - recipientWieners
                    if (int(donation[1]) > donorWieners):
                        message = "Insufficient Wiener Count!"
                    elif (int(donation[1]) > allowance):
                        self.nameList[recipient].wienerLevel += allowance
                        self.nameList[donor].wienerLevel -= allowance
                        message = name + " donates " + str(allowance) + " wieners to " + donation[2]
                    else:
                        self.nameList[recipient].wienerLevel += int(donation[1])
                        self.nameList[donor].wienerLevel -= int(donation[1])
                        message = name + " donates " + str(donation[1]) + " wieners to " + donation[2]
        self.msg(self.chatroom, message)

    def displayWinningWords(self, name):
        player_index = self.getUserIndex(name)
        if player_index is -1:
            return

        word_string = self.getWinningWords(player_index)
        if (word_string is not ""):
            self.msg(self.chatroom, '{}\'s winning words:'.format(name))
            self.msg(self.chatroom, word_string)
        else:
            self.msg(self.chatroom, '{} has no winning words.'.format(name))
            self.showLoserMsg(name)

    def getWinningWords(self, player_index):
        word_string = ", ".join(self.nameList[player_index].wordsWon)
        return word_string

    def showLoserMsg(self, name):
        self.msg(self.chatroom, 'LOSER: {}'.format(name))

    def displayLosers(self):
        self.msg(self.chatroom, 'Here is a list of losers.')
        self.msg(self.chatroom, self.getLoserString())

    @staticmethod
    def getCurrentTime():
        time = match('^(\d+):(\d+)', str(datetime.now().time()))
        day = datetime.today().weekday()
        return ("{}:{}:{}".format(time.group(1), time.group(2), day))

    def getUserIndex(self, name):
        for index in range(len(self.nameList)):
            if self.nameList[index].username == name:
                return (index)
        return (-1)

    def createNewUser(self, name):
        self.nameList.append(Player(name))
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
        print("FileFound")
        self.restoreScores(users)
        return

    def restoreScores(self, users):
        for user in users:
            user = user.split(':')
            index = self.handleUser(user[0])
            self.nameList[index].timesWon = int(user[1])
            self.nameList[index].wienerLevel = int(user[3])
            self.nameList[index].dayOfLastWiener = int(user[4])
            self.nameList[index].wordsWon = ast.literal_eval(user[2])

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

    def whowho(self, ch):
        self.sendLine('WHO %s' % ch)

    def irc_RPL_WHOREPLY(self, *nargs):
        print("WHO: {}".format(nargs))

    def irc_RPL_WHOISUSER(self, *nargs):
        "Receive WHOIS reply from server"
        "nargs in the format:"
        "(Server, [user-who-called-whois, username, hostname, IP, '*', realname])"
        ip = nargs[1][3]
        user = nargs[1][1]
        username = nargs[1][2]
        print('WHOIS: {}'.format(ip))
        self.lastWHOIS = ip
        if (self.muteMode == 'mute'):
            self.mute2(ip)
        elif (self.muteMode == 'unmute'):
            self.unmute2(ip)
        elif (self.muteMode == 'just a whois'):
            for i in range(0, len(nargs)):
                print(nargs[i])
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
        self.checkResetWieners()
        if ((channel == self.chatroom) or (user.split('@')[1] in self.admin)):
            try:
                if (not self.gameRunning and self.userPermaMocked(user.split('!')[0])):
                    self.msg(self.chatroom, self.mockMe(message))
                if (self.gameRunning and int(message) != self.currentNumber):
                    print("[{}] {}: {}".format(str(datetime.now().time()), user, message))
                elif (not self.gameRunning and self.timestampBuffer > 0):
                    print("[{}] {}: {} LATE".format(str(datetime.now().time()), user, message))
                    self.timestampBuffer -= 1
                if (int(message) == self.currentNumber and self.gameRunning):
                    print("[{}] {}: {} COUNTED".format(str(datetime.now().time()), user, message))
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
                        self.adminCommands(user.split('!')[0], message)
                    elif (user.split('@')[1] in self.mutedList):
                        return
                    elif (user.split('!')[1].split('@')[0] in self.botList):
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
            print(user)
        return


class Player:
    numbersAdded = 0
    timesWon = 0
    wienerLevel = 0
    username = ""
    isKicked = False
    hasNewWieners = False
    dayOfLastWiener = -1
    permaMock = False
    wordsWon = []

    def __init__(self, name):
        self.username = name


def main():
    f = protocol.ReconnectingClientFactory()
    f.protocol = CountBot

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()


if __name__ == "__main__":
    main()
