#!/usr/bin/python

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from datetime import datetime
from random import shuffle, randint
from re import match, search
import time

serv_ip = "10.4.163.34"
serv_port = 6667

honkList = [
    "honk",
    "Honk",
    "honk honk",
    "honk honk honk",
    "HHOONNKK",
    "HHHOOONNNKKK",
    "HOOOOOOONNNNNNNNKKKKKKK",
    "honk honk honk honk honk honk honk honk honk honk honk honk honk honk honk honk",
    "Honk Honk!",
    "*beep*",
    "daHonk",
    "hjonk",
]

botName = 'gooseBot'

class gooseBot(irc.IRCClient):
    nickname = "gooseBot"
    chatroom = "#main"
    admin = ["jlogerqu@jlogerqubox.adtran.com"]
    timeLastNickChange = 0
    timeLastPM = 0
    foundNick = False
    hasMocked = True
    ignoreUser = ""
    lastNick = ""

    def signedOn(self):
        self.join(self.chatroom)

    def userRenamed(self, oldname, newname):
        if (oldname.decode('utf-8').lower() != newname.decode('utf-8').lower() and oldname.decode('utf-8').lower() != self.lastNick):
            self.changeNick(oldname)

    def userQuit(self, user, quitMessage):
        self.changeNick(user.split("!")[0])

    def changeNick(self, name):
        self.setNick(name)
        self.honk(self.chatroom)

    def privmsg(self, user, channel, message):
        nick = user.split('!')[0]
        ip = user.split('@')[1]
        if (channel == self.nickname and ip not in self.admin):
            print "<" + str(datetime.now().time()) + "> " + nick + ": " + message
            timeRightNow = time.time()
            if ((timeRightNow - self.timeLastPM) > 30):
                self.msg(nick, "Honk Honk!")
                self.timeLastPM = time.time()
                self.hasMocked = False
            elif self.hasMocked == False:
                self.msg(nick, "HOOOOONNNNKKKKKK!")
                self.hasMocked = True
        if (channel == self.nickname and ip in self.admin):
            msg = message.split()
            if "!op" in msg[0]:
                if msg[1]:
                    print "Opping user <" + msg[1] + ">"
                    self.mode(self.chatroom, True, "o", user=msg[1])
            elif "!deop" in msg[0]:
                if msg[1]:
                    print "De-opping user <" + msg[1] + ">"
                    self.mode(self.chatroom, False, "o", user=msg[1])
            else:
                self.msg(self.chatroom, message)
        if (channel == self.chatroom):
            msg = message.split()
            if 
            if self.nickname in msg[0] or botName in msg[0]:
                if ip in self.admin:
                    if "nick" in msg[1].lower():
                        if msg[2]:
                            self.setNick(msg[2])

                if search(r'bad\s+goose', message) or search(r'give\s+that\s+back', message):
                    self.lastNick = self.nickname
                    self.setNick(botName)
                    self.honk(self.chatroom)
                    self.describe(self.chatroom, "wanders away")

            elif self.checkForHonk(message):
                self.honk(self.chatroom)

    def honk(self, room):
        self.msg(room, honkList[randint(0,len(honkList)-1)])

    def checkForHonk(self,msg):
        for i in ["hjonk","honk","goose","byleth"]:
            if i in msg.lower()
                return True
        return False

    @staticmethod
    def getCurrentTime():
        time = match(r'^(\d+):(\d+)', str(datetime.now().time()))
        return (time.group(1) + ":" + time.group(2))

def main():
    f = protocol.ReconnectingClientFactory()
    f.protocol = gooseBot

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()


if __name__ == "__main__":
    main()
