from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from datetime import datetime
from re import match
import time

serv_ip = "coop.test.adtran.com"
serv_port = 6667

class LurkBot(irc.IRCClient):
    nickname = "lurkBot"
    username = "bhacker"
    chatroom = "#main"
    admin = ["172.22.117.48", "172.22.116.80"]
    namesList = [
                    "awest",
                    "benji",
                    "berNs",
                    "cramey",
                    "emturn",
                    "Isaiah",
                    "jlong",
                    "jnguyen",
                    "kmarcrum",
                    "ldavis",
                    "meena",
                    "mfoley",
                    "mina733",
                    "noahsiano",
                    "story",
                    "tb",
                    "The_OG_Grant",
                    "vshouse"
                ]
    timeLastNickChange = 0
    index = 0
    foundNick = False

    def signedOn(self):
        self.join(self.chatroom)
        self.who()

    def userRenamed(self, oldname, newname):
        if (oldname.decode('utf-8').lower() != newname.decode('utf-8').lower()):
            self.changeNick(oldname)

    def userQuit(self, user, quitMessage):
        currentHour = int(self.getCurrentTime().split(':')[0])
        if ((currentHour <= 8) or (currentHour >= 17)):
            self.changeNick(user.split("!")[0])

    def changeNick(self, name):
        timeRightNow = time.time()
        if (((timeRightNow - self.timeLastNickChange) > 900) and (name in self.namesList)):
            self.timeLastNickChange = time.time()
            self.setNick(name)

    def who(self):
        "Get the user's name, hostname, and IP Address"
        "usage: client.whois('testUser')"
        print "Trying user: " + self.namesList[self.index]
        if (self.foundNick):
            print "No user found."
            print "USING " + self.namesList[self.index]
            self.setNick(self.namesList[self.index])
            self.foundNick = True
        if (self.foundNick == False):
            self.foundNick = True
            self.index += 1
            if len(self.namesList) > self.index:
                self.sendLine('WHOIS %s' % self.namesList[self.index])
            else:
                print "No nick usable."
                self.setNick("oops")

    def irc_RPL_WHOISUSER(self, *nargs):
        username = nargs[1][1]
        print "Found user: " + username
        self.foundNick = False

    def irc_RPL_ENDOFWHOIS(self, prefix, args):
        self.who()

    def nickChanged(self, nick):
        print "New nickname: " + nick
        self.nickname = nick

    def privmsg(self, user, channel, message):
        nick = user.split('!')[0]
        ip = user.split('@')[1]
        if (channel == self.nickname and ip not in self.admin):
            print "lol " + nick + " just said " + message
            self.msg(nick, "Just lurking here... Don't mind me...")
        if (channel == self.nickname and ip in self.admin):
            self.msg(self.chatroom, message)

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
