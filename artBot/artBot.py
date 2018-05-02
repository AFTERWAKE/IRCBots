"""
==============================================================================================================================

           Name: artBot
         Author: ldavis
Current Version: 1.3.5
   Date Written: February 2018
    Description: A simple irc bot that prints out from a selection of ASCII art messages, along with a calming quote by
        the one and only Bob Ross. artBot also sends out a message whenever lunchtime or break arrives. The structure of
        artBot was inspired by jnguyen's work on Seahorse and MemeBot, and also noahsiano's current revision of theCount.

==============================================================================================================================
"""

import random
import re
import json

import datetime

from twisted.words.protocols import irc
from twisted.internet import task, reactor, protocol

with open(r'config.json') as file:
    config = json.load(file)

class ArtBot(irc.IRCClient):
    nickname = config['nick']

    def __init__(self):
        self.painting = False
        self.lunchtimePaintingQueued = False
        self.breaktimePaintingQueued = False

        self.tags = []
        self.loadTags()

        lc = task.LoopingCall(self.scheduleEvents)
        lc.start(60)

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
        message = irc.stripFormatting(message)
        
        if self.isHelpCommand(message):
            self.printHelpMessage()
        elif self.isListTagsCommand(message):
            self.printTags()
        elif self.isPaintCommand(message):
            args = message.split()
            
            if len(args) == 2:
                self.paintMessageRandom()
            else:
                self.paintMessageByTag(args[2])

    def isHelpCommand(self, message):
        return re.match('^' + config['nick'] + ',\s+help$', message)

    def isListTagsCommand(self, message):
        return re.match('^' + config['nick'] + ',\s+list-tags$', message)

    def isPaintCommand(self, message):
        return re.match('^' + config['nick'] + ',\s+paint.*$', message)

    def printHelpMessage(self):
        if self.painting:
            return

        self.msg(config['channel'], 'Please use one of the following commands:')
        self.msg(config['channel'], 'artBot, help: Ask me for help')
        self.msg(config['channel'], 'artBot, paint <tag>: Paint ASCII message by tag (random by default)')
        self.msg(config['channel'], 'artBot, list-tags: Lists all message tags for painting')

    def printTags(self):
        if self.painting:
            return

        self.msg(config['channel'], 'Here is a list of available tags (artBot, paint <tag>):')
        
        line = ', '.join(sorted(self.tags))
        self.msg(config['channel'], line)

    def paintLunchtimeMessage(self):
        if self.painting:
            self.lunchtimePaintingQueued = True
            return

        self.paintMessage(config['lunchtime-painting'])

    def paintBreaktimeMessage(self):
        if self.painting:
            self.breaktimePaintingQueued = True
            return

        self.paintMessage(config['breaktime-painting'])

    def paintMessageRandom(self):
        painting = random.choice(config['paintings'])
        self.paintMessage(painting['message'])

    def paintMessageByTag(self, tag):
        for painting in config['paintings']:
            if re.match('^' + tag + '$', painting['tag']):
                self.paintMessage(painting['message'])
                break

    def paintMessage(self, message):
        if self.painting:
            return

        numSeconds = 0
        reactor.callLater(numSeconds, self.enablePainting)

        for msg in message:
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

    def scheduleEvents(self):
        if self.lunchtimePaintingQueued:
            self.lunchtimePaintingQueued = False
            self.paintLunchtimeMessage()
            return
        elif self.breaktimePaintingQueued:
            self.breaktimePaintingQueued = False
            self.paintBreaktimeMessage()
            return

        now = datetime.datetime.time(datetime.datetime.now())

        lunchtime = datetime.time(hour=11, minute=30)
        breaktime = datetime.time(hour=15, minute=0)

        if now.hour == lunchtime.hour and now.minute == lunchtime.minute:
            self.paintLunchtimeMessage()
        elif now.hour == breaktime.hour and now.minute == breaktime.minute:
            self.paintBreaktimeMessage()

def main():
    server = config['server']
    port = 6667

    client = protocol.ClientFactory()
    client.protocol = ArtBot

    reactor.connectTCP(server, port, client)
    reactor.run()

if __name__ == '__main__':
    main()
