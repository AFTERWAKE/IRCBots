"""
==============================================================================================================================

           Name: artBot
         Author: ldavis
Current Version: 1.2.4
   Date Written: February 2018
    Description: A simple irc bot that prints out from a selection of ASCII art messages, along with a calming quote by
        the one and only Bob Ross. The structure of artBot was inspired by jnguyen's work on Seahorse and MemeBot, and also
        noahsiano's current revision of theCount.

==============================================================================================================================
"""

import random
import re
import json

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

with open(r'config.json') as file:
    config = json.load(file)

class ArtBot(irc.IRCClient):
    nickname = config['nick']

    def __init__(self):
        self.painting = False

        self.tags = []
        self.loadTags()

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
        if self.isHelpCommand(message):
            self.printHelpMessage()
        elif self.isListCommand(message):
            self.printTags()
        elif self.isPaintCommand(message):
            args = message.split()
            
            if len(args) == 2:
                self.paintMessageRandom()
            else:
                self.paintMessageByTag(args[2])

    def isHelpCommand(self, message):
        return re.match('^' + config['nick'] + ',\s+help$', message)

    def isListCommand(self, message):
        return re.match('^' + config['nick'] + ',\s+list$', message)

    def isPaintCommand(self, message):
        return re.match('^' + config['nick'] + ',\s+paint.*$', message)

    def printHelpMessage(self):
        if self.painting:
            return

        self.msg(config['channel'], 'Please use one of the following commands:')
        self.msg(config['channel'], 'artBot, help: Ask me for help')
        self.msg(config['channel'], 'artBot, paint <tag>: Paint ASCII message by its corresponding tag (random by default)')
        self.msg(config['channel'], 'artBot, list: Lists all of the valid message tags for painting')

    def printTags(self):
        if self.painting:
            return

        self.msg(config['channel'], 'Here is a list of available tags (artBot, paint <tag>):')
        
        line = ', '.join(sorted(self.tags))
        self.msg(config['channel'], line)

    def paintMessageRandom(self):
        painting = random.choice(config['paintings'])
        self.paintMessage(painting)

    def paintMessageByTag(self, tag):
        for painting in config['paintings']:
            if re.match('^' + tag + '$', painting['tag']):
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

    def loadTags(self):
        for painting in config['paintings']:
            self.tags.append(painting['tag'])

def main():
    server = config['server']
    port = 6667

    client = protocol.ClientFactory()
    client.protocol = ArtBot

    reactor.connectTCP(server, port, client)
    reactor.run()

if __name__ == '__main__':
    main()
