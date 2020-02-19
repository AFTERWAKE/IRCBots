#!/usr/bin/python

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from re import search, IGNORECASE
from random import randint
import random
import enchant


serv_ip = "10.4.163.34"
serv_port = 6667
d = enchant.Dict("en_US")

values = {
    'a': 1,  'b': 3, 'c': 3, 'd': 2,
    'e': 1,  'f': 4, 'g': 2, 'h': 4,
    'i': 1,  'j': 8, 'k': 5, 'l': 1,
    'm': 3,  'n': 1, 'o': 1, 'p': 3,
    'q': 10, 'r': 1, 's': 1, 't': 1,
    'u': 1,  'v': 4, 'w': 4, 'x': 8,
    'y': 4,  'z': 10
}

class ScrabbleBot(irc.IRCClient):
    nickname = "ScrabbleBot"
    chatroom = "#main"


    def signedOn(self):
        self.join(self.chatroom)

    def getValue(self, char):
        return values[char]

    def computeScore(self, word):
        score = 0;
        for c in range(len(word)):
            if word[c].isalpha():
                score += values[word[c].lower()]
        return score

    def printValues(self):
        return "a: 1,  b: 3,  c: 3,  d: 2,  e: 1,  f: 4,\n" \
               "g: 2,  h: 4,  i: 1,  j: 8,  k: 5,  l: 1,\n" \
               "m: 3,  n: 1,  o: 1,  p: 3,  q: 10, r: 1,\n" \
               "s: 1,  t: 1,  u: 1,  v: 4,  w: 4,  x: 8,\n" \
               "y: 4,  z: 10"

    def privmsg(self, user, channel, message):
        if(channel == self.chatroom):
            if (message.startswith(self.nickname)):
                temp = message.split()
                if (len(temp) > 1):
                    if (len(temp[1]) > 0):
                        if (temp[1].lower() == 'help'):
                            self.msg(self.chatroom, "Give me a word and I will return that word's Scrabble score. Example: \"" + self.nickname + ", [word]\" I also point out exceptional words!")
                        elif (temp[1].lower() == 'points'):
                            valstring = str(values)
                            self.msg(self.chatroom, "Point values: \n" + self.printValues())
                        else:
                            val = self.computeScore(temp[1])
                            if(not d.check(temp[1])):
                                self.msg(self.chatroom, temp[1] + " is not a valid word. Reason: was not found in dictionary.")
                            elif (len(temp[1]) > 15):
                                self.msg(self.chatroom, temp[1] + " is not a valid word. Reason: too many letters (max 15).")
                            else:
                                self.msg(self.chatroom, temp[1] + ": " + str(val) + " points")
            else:
                temp = message.split()
                for word in temp:
                    if(d.check(word)):
                        if(len(word) > 5 and len(word) < 16):
                            val = self.computeScore(word)
                            if(float(val)/float(len(word)) > 2.5):
                                self.msg(self.chatroom, word + ": " + str(val) + " points")


def main():
    f = protocol.ReconnectingClientFactory()
    f.protocol = ScrabbleBot

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()


if __name__ == "__main__":
    main()
