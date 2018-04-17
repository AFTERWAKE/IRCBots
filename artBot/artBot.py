"""
==============================================================================================================================

        Name: artBot
      Author: ldavis
Date Written: February 2018
 Description: A simple irc bot that sends out a random ASCII art message at 11:30 and 3:00, along with a calming quote by
        the one and only Bob Ross. The structure of artBot was inspired by jnguyen's work on Seahorse and MemeBot, and also
        noahsiano's current revision of theCount.

==============================================================================================================================
"""

import random
import re
import json

import time

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

with open(r'config.json') as file:
    config = json.load(file)

class ArtBot(irc.IRCClient):
    nickname = config['nick']

    def __init__(self):
        self.painting = False

    def signedOn(self):
        self.join(config['channel'])
        print('Channel: ' + config['channel'])
        print('Nickname: ' + config['nick'])
    
    def luserClient(self, info):
        print(info)

    def userJoined(self, user, channel):
        print('Joined:', channel, user)

    def userLeft(self, user, channel):
        print('LEFT:', channel, user)

    def userQuit(self, user, quitMessage):
        print('QUIT:', user)

    def userRenamed(self, oldName, newName):
        print(oldName + ' has been renamed to ' + newName)

    def privmsg(self, user, channel, message):
        #if re.split('!', user)[0] != config['admin']:
        #    print('Invalid user: ' + user)
        #    return

        if re.match(config['nick'] + ', paint', message):
            arg = re.split(', paint', message)[1]
            
            if arg == '':
                painting = random.choice(config['paintings'])
                self.paintMessage(painting)
            else:
                for painting in config['paintings']:
                    if re.match(arg, ' ' + painting['tag']):
                        self.paintMessage(painting)
                    break

    def paintMessage(self, painting):
        if self.painting:
            return

        numSeconds = 0
        reactor.callLater(numSeconds, self.enablePainting)

        for msg in painting['message']:
            reactor.callLater(numSeconds, self.printDelayedMessage, msg)
            numSeconds += 2

        reactor.callLater(numSeconds, self.printDelayedMessage, self.getQuote())
        reactor.callLater(numSeconds, self.disablePainting)

    def getQuote(self):
        quote = random.choice(config['quotes'])
        return quote + ' - Bob Ross'

    def printDelayedMessage(self, message):
        self.msg(config['channel'], message)

    def enablePainting(self):
        self.painting = True

    def disablePainting(self):
        self.painting = False

def main():
    server = config['server']
    port = 6667

    client = protocol.ClientFactory()
    client.protocol = ArtBot

    reactor.connectTCP(server, port, client)
    reactor.run()

if __name__ == '__main__':
    main()
