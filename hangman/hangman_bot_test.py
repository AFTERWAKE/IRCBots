import random


from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, defer
from re import search, IGNORECASE
from random import (
                    choice,
                    randint
                    )
import random
import time
import os

serv_ip = "coop.test.adtran.com"
serv_port = 6667


class hangman(irc.IRCClient):

    nickname = "hangman_teset"
    channel = "#hangmantest"
    owner = 'tarp-coop-ubuntu.adtran.com'
    owner_name = ""
    currentTime = 0
    default = 'burn berNs'
    botList = [
        "dad", "Seahorse", "pointbot", "botProtector",
        "QuipBot", "MemeBot", "theCount", "Doge", "Calculator", "complimentBot"]
    user_list = []
    ignoreList = []

    wordRemoving = "" #used to see where the dashed should be replaced on the display
    word = "" #the word, doesn't get changed once assigned
    wordWorking = "" #contains the dashes and is diplayed and updated as the user guesses
    wordLength = 0
    usedChars = "" #guessed characters
    hangmanEmpty = "   ____\n  |    |\n  |\n  |\n  |\n__|__"
    hangman1 = "   ____\n  |    |\n  |   ( )\n  |\n  |\n__|__"
    hangman2 = "   ____\n  |    |\n  |   ( )\n  |    |\n  |\n__|__"
    hangman3 = "   ____\n  |    |\n  |   ( )\n  |   \|\n  |\n__|__"
    hangman4 = "   ____\n  |    |\n  |   ( )\n  |  '\|\n  |\n__|__"
    hangman5 = "   ____\n  |    |\n  |   ( )\n  |  '\|/\n  |\n__|__"
    hangman6 = "   ____\n  |    |\n  |   ( )\n  |  '\|/'\n  |\n__|__"
    hangman7 = "   ____\n  |    |\n  |   ( )\n  |  '\|/'\n  |   /\n__|__"
    hangman8 = "   ____\n  |    |\n  |   ( )\n  |  '\|/'\n  |  _/\n__|__"
    hangman9 = "   ____\n  |    |\n  |   ( )\n  |  '\|/'\n  |  _/ \\\n__|__"
    hangman10 = "   ____\n  |    |\n  |   ( )\n  |  '\|/'\n  |  _/ \\_\n__|__"
    
    allowedWrongGuesses = 10 
    wrongGuesses = 0
    rightGuesses = 0
    continuePlaying = True
    gameRunning = False
    nextUser = 0

    def signedOn(self):
        self.join(self.channel)
        self.who(self.channel)

    def who(self, channel):
        "List the users in 'channel', usage: client.who('#testroom')"
        self.user_list = []
        self.sendLine('WHO %s' % channel)

    def irc_RPL_WHOREPLY(self, *nargs):
        "Receive WHO reply from server"
        usr = {}
        finUsr = {}
        usr["nick"] = nargs[1][5]
        usr["host"] = nargs[1][2]
        usr["ip"] = nargs[1][3]
        if (usr["ip"] == self.owner):
               self.owner_name = usr["nick"]
        self.user_list.append(usr)

      
    def irc_RPL_ENDOFWHO(self, *nargs):
            "Called when WHO output is complete"
            self.msg(self.channel, "Users:")
            for each in self.user_list:
                self.msg(self.channel, each["nick"] + each["ip"])

    
    def privmsg(self, user, channel, message):
		
        timeRightNow = time.time()
        nick = user.split('!')[0]
        user_ip = user.split('@')[1]
        user_name = []
        for name in self.user_list: user_name.append(name["nick"])

        if (search(r'(^|\s)+help *(\s|$)+', message, IGNORECASE)):
            self.currentTime = time.time()
            self.msg(self.channel, "Hi! I am a little hangman game made by Ashleigh. Enter a character when I ask and try to solve the word before DEATH. To start, enter \"play\"")
        

        if (message == "play"):
            self.wrongGuesses = 0
            self.rightGuesses = 0
            self.wordRemoving = ""
            self.word = ""
            self.wordWorking = ""
            self.usedChars = ""
            self.nextUser = 0
            self.currentTime = time.time()
            self.msg(self.channel, "starting game")
            self.msg(self.channel, nick + ": you start")
            self.gameRunning = True
            self.pickWord()
            print (self.word)
            self.generateString()
            self.showGame()
            return
        
        picked = self.user_list[self.nextUser]
        if ("hangman_tese" in picked):
            picked = self.user_list[self.nextUser + 1]
        self.nextUser = self.nextUser + 1

        if(len(message) == 1):
            print(message)
            if(not self.checkAlreadyUsed(message)):
                self.checkInput(message)
            self.currentTime = time.time()
            self.msg(self.channel, str(picked) + ": your turn!")
            return
        
    #pick word function
    def pickWord(self):
        self.currentTime = time.time()
        lines = open('words.txt').read().splitlines()
        myline =random.choice(lines)
        self.word = myline
        self.wordRemoving = self.word

    #generate array of underscores function
    def generateString(self):
        self.currentTime = time.time()
        i = 1
        dash = "-"
        self.wordWorking = "-"
        while (i < len(self.word)):
            self.wordWorking = self.wordWorking + dash
            i = i + 1
        print(self.wordWorking)

    def checkAlreadyUsed(self, userInput):
        if (userInput in self.usedChars):
            self.currentTime = time.time()
            self.msg(self.channel, userInput + " already guessed, go again\n")
            return True
        else:
            return False
        
    #check if input is in word
    def checkInput(self, userInput):
        print("WordRemoving = " + self.wordRemoving)
        inputValid = userInput in self.wordRemoving
        if(self.wrongGuesses == 0 and self.rightGuesses == 0):
            self.usedChars = userInput
        else:
            self.usedChars = self.usedChars + ", " + userInput
    
        if(inputValid and (self.rightGuesses < len(self.word))):
            self.correctInput(userInput)
        elif(inputValid and (self.rightGuesses == len(self.word))):
            self.theyWin()
        elif(not inputValid and (self.wrongGuesses <= self.allowedWrongGuesses)):
            self.incorrectInput(userInput)
        elif(not inputValid and (self.wrongGuesses > self.allowedWrongGuesses)):
            self.theyLose()
    
    #show game board
    def showGame(self):
        print("word working = " + self.wordWorking)
        if(self.wrongGuesses == 0):
            self.currentTime = time.time()
            self.msg(self.channel, self.hangmanEmpty)
            self.msg(self.channel, "Characters used: " + self.usedChars)
            self.msg(self.channel, self.wordWorking)
        elif(self.wrongGuesses == 1):
            self.currentTime = time.time()
            self.msg(self.channel, self.hangman1)
            self.msg(self.channel, "Characters used: " + self.usedChars)
            self.msg(self.channel, self.wordWorking)
        elif(self.wrongGuesses == 2):
            self.currentTime = time.time()
            self.msg(self.channel, self.hangman2)
            self.msg(self.channel, "Characters used: " + self.usedChars)
            self.msg(self.channel, self.wordWorking)
        elif(self.wrongGuesses == 3):
            self.currentTime = time.time()
            self.msg(self.channel, self.hangman3)
            self.msg(self.channel, "Characters used: " + self.usedChars)
            self.msg(self.channel, self.wordWorking)
        elif(self.wrongGuesses == 4):
            self.currentTime = time.time()
            self.msg(self.channel, self.hangman4)
            self.msg(self.channel, "Characters used: " + self.usedChars)
            self.msg(self.channel, self.wordWorking)
        elif(self.wrongGuesses == 5):
            self.currentTime = time.time()
            self.msg(self.channel, self.hangman5)
            self.msg(self.channel, "Characters used: " + self.usedChars)
            self.msg(self.channel, self.wordWorking)
        elif(self.wrongGuesses == 6):
            self.currentTime = time.time()
            self.msg(self.channel, self.hangman6)
            self.msg(self.channel, "Characters used: " + self.usedChars)
            self.msg(self.channel, self.wordWorking)
        elif(self.wrongGuesses == 7):
            self.currentTime = time.time()
            self.msg(self.channel, self.hangman7)
            self.msg(self.channel, "Characters used: " + self.usedChars)
            self.msg(self.channel, self.wordWorking)
        elif(self.wrongGuesses == 8):
            self.currentTime = time.time()
            self.msg(self.channel, self.hangman8)
            self.msg(self.channel, "Characters used: " + self.usedChars)
            self.msg(self.channel, self.wordWorking)
        elif(self.wrongGuesses == 9):
            self.currentTime = time.time()
            self.msg(self.channel, self.hangman9)
            self.msg(self.channel, "Characters used: " + self.usedChars)
            self.msg(self.channel, self.wordWorking)
        elif(self.wrongGuesses == 10):
            self.currentTime = time.time()
            self.msg(self.channel, self.hangman10)
            self.msg(self.channel, "Characters used: " + self.usedChars)
            self.msg(self.channel, self.wordWorking)



        self.currentTime = time.time()
        self.msg(self.channel, "Enter a character:")
        
    
    #user gave correct input, update string
    def correctInput(self, userInput):
        self.rightGuesses = self.rightGuesses + 1
        self.currentTime = time.time()
        self.msg(self.channel, "Right! :D Your guess " + userInput + " is in the word.\n")
        
        
        while(userInput in self.wordRemoving):
            index = self.wordRemoving.find(userInput)
            l1 = list(self.wordRemoving)
            l1[index] = '*'
            self.wordRemoving = "".join(l1)
    
            l2 = list(self.wordWorking)
            l2[index] = userInput
            self.wordWorking = "".join(l2)
        
        if(self.wordWorking == self.word):
            self.theyWin()
        else:
            self.showGame()

    #user gave last correct input, they win
    def theyWin(self):
        self.continuePlaying = False
        self.gameRunning = False
        self.currentTime = time.time()
        self.msg(self.channel, "`~`~` Congrats!!!! You got the winning word: " + self.word + "!!!!`~`~`")
        self.msg(self.channel, "To reset and play again, enter \"play\"!")
        
    
    #user gave incorrect input, edit hangman and incorrect guesses
    def incorrectInput(self, userInput):
        remaining = self.allowedWrongGuesses - self.wrongGuesses
        self.wrongGuesses = self.wrongGuesses + 1
        if(remaining > 0):
            self.currentTime = time.time()
            self.msg(self.channel, "Wrong >:( Your guess " + userInput + " is not in the word. Mr. Hangman gets another body part.\n")
            if(remaining <= 4):
                self.currentTime = time.time()
                self.msg(self.channel, "Warning!!! Only " + str(remaining) + " wrong guesses remaining!")
            self.showGame()
        else:
            self.theyLose()
        
    
    #user maxed out guesses, they lose
    def theyLose(self):
        self.continuePlaying = False
        self.gameRunning = False
        self.currentTime = time.time()
        self.msg(self.channel, "\n\nboi you dun goofed and hangman is ded. Winning word was: " + self.word)
        self.msg(self.channel, "To reset and play again, enter \"play\"!")

        
    #play again?
    def playAgain(self, message):
        self.currentTime = time.time()
        self.msg(self.channel, "Do you want to play again? (y/n): ")
        if search(r'(^|\s)+idea *(\s|$)+', message, IGNORECASE):
            self.currentTime = time.time()
            self.msg(self.channel, "Yay!! Here we go again!!!!!")
            self.continuePlaying = True
            self.playGame(message)
        else:
            self.currentTime = time.time()
            self.msg(self.channel, "Baiiiii")
    
    
def main():
    f = protocol.ReconnectingClientFactory()
    f.protocol = hangman
    
    reactor.connectTCP("coop.test.adtran.com", 6667, f)
    reactor.run()

while 1:
    main()