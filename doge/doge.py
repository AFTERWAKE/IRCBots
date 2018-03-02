from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from re import search, IGNORECASE
import time

serv_ip = "coop.test.adtran.com"
serv_port = 6667

class Doge(irc.IRCClient):
    nickname = "Doge"
    chatroom = "#main"
    timeLastCommand = 0

    def signedOn(self):
        self.join(self.chatroom)

    def privmsg(self, user, channel, message):
        if (search(r"(^|\s)+wow!*(\s|$)+", message, IGNORECASE) or
        search(r"(^|\s)+very(\s|$)+", message, IGNORECASE) or
        search(r"(^|\s)+such(\s|$)+", message, IGNORECASE)):
            timeRightNow = time.time()
            if (timeRightNow - self.timeLastCommand) > 5:
                self.timeLastCommand = time.time()
                self.msg(self.chatroom, "Wow!")








def main():
    f = protocol.ReconnectingClientFactory()
    f.protocol = Doge

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()


if __name__ == "__main__":
    main()
