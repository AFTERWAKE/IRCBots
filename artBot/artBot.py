'''
==============================================================================================================================

        Name: artBot
      Author: ldavis
Date Written: February 2018
 Description: A simple irc bot that sends out a random ASCII art message at 11:30 and 3:00, along with a calming quote by
        the one and only Bob Ross. The structure of artBot was inspired by jnguyen's work on Seahorse and memeBot, and also
        noahsiano's current revision of theCount.

==============================================================================================================================
'''

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

    def signedOn(self):
        self.join(config['channel'])
        print('Channel: ' + config['channel'])
        print('Nickname: ' + config['nick'])
        #self.msg(config['channel'], "Hello, I'm artbot.")
        #time.sleep(1)
        #self.msg(config['channel'], "How do you do?")
    
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
        print(channel + ' ' + user + ': ' + message)

        if re.split('!', user)[0] != config['admin']:
            print(user)
            print('Invalid user!')
            return

        if re.match(config['nick'] + ', paint', message):
            print('Matched command!')
            print('Channel: ' + channel)
            print('Config Channel: ' + config['channel'])
            #self.msg(channel, 'Matched!')
            
            arg = re.split(', paint', message)[1]
            
            quote = random.choice(config['quotes'])

            if arg == '':
                with random.choice(config['paintings']) as painting:
                    for msg in painting['message']:
                        self.msg(config['channel'], msg)
                    self.msg(channel, quote + ' - Bob Ross')
            else:
                for painting in config['paintings']:
                    print(arg)
                    print(painting['tag'])
                    if re.match(arg, ' ' + painting['tag']):
                        print('found!')
                        for msg in painting['message']:
                            print(msg)
                            self.msg(config['channel'], msg)
                            time.sleep(1)
                            print('hello.')
                        self.msg(channel, quote + ' - Bob Ross')

def main():
    server = config['server']
    port = 6667

    client = protocol.ClientFactory()
    client.protocol = ArtBot

    reactor.connectTCP(server, port, client)
    reactor.run()

if __name__ == '__main__':
    main()
