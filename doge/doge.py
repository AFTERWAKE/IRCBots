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
    owner = ["172.22.117.48", "172.22.116.80"]

    def signedOn(self):
        self.join(self.chatroom)

    def privmsg(self, user, channel, message):
        if (message.startswith(self.nickname)):
            if (user.split('@')[1] in self.owner):
                if message == (self.nickname + ', sit'):
                    self.describe(self.chatroom, "sits")
                if message == (self.nickname + ', roll over'):
                    self.describe(self.chatroom, "rolls over")
                if message == (self.nickname + ', shake'):
                    self.describe(self.chatroom, "lifts up paw")
                if message == (self.nickname + ', play dead'):
                    self.describe(self.chatroom, "lays down dramatically")
        if search(r"(^|\s)+treats*(!|\?)*(\s|$)+", message, IGNORECASE):
            timeRightNow = time.time()
            if (timeRightNow - self.timeLastCommand) > 5:
                self.timeLastCommand = time.time()
                self.describe(self.chatroom, "perks his head up")
        elif search(r"(^|\s)+good boy!*(\s|$)+", message, IGNORECASE):
            timeRightNow = time.time()
            if (timeRightNow - self.timeLastCommand) > 5:
                self.timeLastCommand = time.time()
                self.describe(self.chatroom, "barks")
        elif (search(r"(^|\s)+wow!*(\s|$)+", message, IGNORECASE) or
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
