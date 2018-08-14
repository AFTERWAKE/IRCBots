from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from datetime import datetime
from random import shuffle
from re import match
import time

serv_ip = "coop.test.adtran.com"
serv_port = 6667

class LurkBot(irc.IRCClient):
    nickname = "lurkBot"
    username = "bhacker"
    chatroom = "#main"
    admin = ["172.22.117.48", "172.22.116.80", "nsiano800w10.adtran.com"]
    namesList = [
                    "awest",
                    "benji",
                    "berNs",
                    "cramey",
                    "chasely",
                    "Isaiah",
                    "jlong",
                    "jnguyen",
                    "kmarcrum",
                    "ldavis",
                    "meena",
                    "mfoley",
                    "mina733",
                    "noahsiano",
                    "sboyett",
                    "story",
                    "tb",
                    "The_OG_Grant",
                    "vshouse"
                ]
    timeLastNickChange = 0
    timeLastPM = 0
    index = 0
    foundNick = False
    hasMocked = True
    ignoreUser = ""

    def signedOn(self):
        shuffle(self.namesList)
        self.join(self.chatroom)
        self.who()

    def userRenamed(self, oldname, newname):
        if (oldname.decode('utf-8').lower() != newname.decode('utf-8').lower()):
            self.changeNick(oldname)

    def userQuit(self, user, quitMessage):
        currentHour = int(self.getCurrentTime().split(':')[0])
        if ((currentHour < 8) or (currentHour > 16)):
            self.changeNick(user.split("!")[0])

    def changeNick(self, name):
        timeRightNow = time.time()
        if (((timeRightNow - self.timeLastNickChange) > 900) and (name in self.namesList)):
            self.timeLastNickChange = time.time()
            self.setNick(name)

    def who(self):
        "Get the user's name, hostname, and IP Address"
        "usage: client.whois('testUser')"
        if self.namesList[self.index] != self.ignoreUser:
            print "Trying user: " + self.namesList[self.index]
            if (self.foundNick):
                print "No user named " + self.namesList[self.index] + " found."
                print "USING " + self.namesList[self.index]
                self.setNick(self.namesList[self.index])
                self.foundNick = True
            if (self.foundNick == False):
                self.foundNick = True
                self.runNewWhoIs()
        else:
            print "Skipping user: " + self.namesList[self.index]
            self.runNewWhoIs()

    def irc_RPL_WHOISUSER(self, *nargs):
        username = nargs[1][1]
        print "Found user: " + username
        self.foundNick = False

    def irc_RPL_ENDOFWHOIS(self, prefix, args):
        self.who()

    def runNewWhoIs(self):
        self.index += 1
        if len(self.namesList) > self.index:
            self.sendLine('WHOIS %s' % self.namesList[self.index])
        else:
            print "No nick usable."
            if self.ignoreUser == "":
                self.setNick("oops")
            else:
                self.msg(self.chatroom, "Looks like there's no other name to steal!")
                self.ignoreUser = ""

    def nickChanged(self, nick):
        print "New nickname: " + nick
        self.nickname = nick

    def privmsg(self, user, channel, message):
        nick = user.split('!')[0]
        ip = user.split('@')[1]
        if (channel == self.nickname and ip not in self.admin):
            print "<" + str(datetime.now().time()) + "> " + nick + ": " + message
            timeRightNow = time.time()
            if ((timeRightNow - self.timeLastPM) > 30):
                self.msg(nick, "Just lurking here... Don't mind me...")
                self.timeLastPM = time.time()
                self.hasMocked = False
            elif self.hasMocked == False:
                self.msg(nick, "IDIOT!")
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
            if self.nickname in msg[0]:
                if ip in self.admin:
                    if "nick" in msg[1].lower():
                        if msg[2]:
                            self.setNick(msg[2])
                if "please" in msg[1].lower() or "please" in msg[-1].lower():
                    timeRightNow = time.time()
                    if (((timeRightNow - self.timeLastNickChange) > 900) and (nick not in self.namesList)):
                        self.msg(self.chatroom, "Fiiiine...")
                        self.timeLastNickChange = time.time()
                        self.index = 0
                        self.foundNick = False
                        self.ignoreUser = self.nickname
                        self.who()

    @staticmethod
    def getCurrentTime():
        time = match('^(\d+):(\d+)', str(datetime.now().time()))
        return (time.group(1) + ":" + time.group(2))

def main():
    f = protocol.ReconnectingClientFactory()
    f.protocol = LurkBot

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()


if __name__ == "__main__":
    main()
