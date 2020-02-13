#!/usr/bin/python

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from re import search, IGNORECASE
from random import randint
import time
import json
import random


serv_ip = "172.22.115.228"
serv_port = 6667

values = {
    'a': 1,  'b': 3, 'c': 3, 'd': 2,
    'e': 1,  'f': 4, 'g': 2, 'h': 4,
    'i': 1,  'j': 8, 'k': 5, 'l': 1,
    'm': 3,  'n': 1, 'o': 1, 'p': 3,
    'q': 10, 'r': 1, 's': 1, 't': 1,
    'u': 1,  'v': 4, 'w': 4, 'x': 8,
    'y': 4,  'z': 10
}

class Hulk(irc.IRCClient):
    nickname = "ScrabbleBot"
    chatroom = "#testing"


    def signedOn(self):
        self.join(self.chatroom)

    def getValue(self, char):
        return values[char]

    def computeScore(self, word):
        score = 0;
        for c in range(len(word)):
            if word[c].isalpha():
                score += values[word[c]]
        return score

    def privmsg(self, user, channel, message):
        if (message.startswith(self.nickname)):
            temp = message.split()
            print(temp)
            if (len(temp) > 1):
                if (len(temp[1]) > 0):
                    if (temp[1].lower() == 'help'):
                        self.msg(self.chatroom, "Give me a word and I will return that word's Scrabble score. Example: \"" + self.nickname + ", [word]\"")
                    else:
                        val = self.computeScore(temp[1])
                        self.msg(self.chatroom, temp[1] + ": " + str(val) + " points")


def main():
    f = protocol.ReconnectingClientFactory()
    f.protocol = Hulk

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()


if __name__ == "__main__":
    main()
