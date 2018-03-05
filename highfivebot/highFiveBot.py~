from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from re import search, IGNORECASE
from random import randint
import time

serv_ip = "coop.test.adtran.com"
serv_port = 6667

class HighFiveBot(irc.IRCClient):
    nickname = "OG_HighFive"
    chatroom = "#main"
    timeLastCommand = 0

    def signedOn(self):
        self.join(self.chatroom)

    def privmsg(self, user, channel, message):
        if (search(r"^\s*o\/\s*$", message, IGNORECASE) or
        search(r"^\s*o\/\/\s*$", message, IGNORECASE) or
        search(r"^\s*\\o\/\s*$", message, IGNORECASE) or
        search(r"^\s*\\o\s*$", message, IGNORECASE) or
        search(r"^\s*\\\\o\s*$", message, IGNORECASE)):
            timeRightNow = time.time()
            if (timeRightNow - self.timeLastCommand) > 4:
                self.timeLastCommand = time.time()
                self.msg(self.chatroom, self.randomResponse(user.split("!")[0]))

    def randomResponse(self, nick):
        responses = [
            nick + ", yeah dude!!! http://i.imgur.com/MAiIwW8.gifv",
            "\\o You Rock, " + nick,
            nick + ", \\o!!!",
            nick + ", http://24.media.tumblr.com/tumblr_m6h84mAoMS1rwcc6bo1_500.gif",
            "\\o you never cease to amaze me, " + nick + "!",
            nick + ", \\o",
            nick + ", wow, just.. wow. \\o",
            "\\o this is just incredible " + nick + "!",
            nick + ", NO. jk! \\o",
            "Tom would be proud of you, " + nick + " \\o",
            "\\o Thanks " + nick + "!!",
            nick + ", http://i.imgur.com/glFDOpL.gif",
            nick + ", http://i.imgur.com/0rpP0bd.gifv",
            nick + ", http://i.imgur.com/WJKWoCK.gif",
            "....fine then " + nick + " http://i.imgur.com/YED5jgK.gif",
            nick + ", https://i.imgur.com/ybNEq8m.gifv"
        ]
        return responses[randint(0,len(responses)-1)]


def main():
    f = protocol.ReconnectingClientFactory()
    f.protocol = HighFiveBot

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()


if __name__ == "__main__":
    main()
