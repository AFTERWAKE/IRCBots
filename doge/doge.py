from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from re import search, IGNORECASE
from random import randint
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
            isOwner = user.split('@')[1] in self.owner
            if isOwner or (randint(0, 3) == 1):
                timeRightNow = time.time()
                if ((timeRightNow - self.timeLastCommand) > 4) or isOwner:
                    self.timeLastCommand = time.time()
                    if message == (self.nickname + ', sit'):
                        self.describe(self.chatroom, "sits")
                    elif message == (self.nickname + ', roll over'):
                        self.describe(self.chatroom, "rolls over")
                    elif message == (self.nickname + ', shake'):
                        self.describe(self.chatroom, "lifts up paw")
                    elif message == (self.nickname + ', play dead'):
                        self.describe(self.chatroom, "lays down dramatically")
                    elif message == (self.nickname + ', speak'):
                        if randint(0, 5) == 1:
                            self.describe(self.chatroom, "borks")
                        else:
                            self.describe(self.chatroom, "borks")
        if search(r"(^|\s)+treats*(!|\?)*(\s|$)+", message, IGNORECASE):
            timeRightNow = time.time()
            if (timeRightNow - self.timeLastCommand) > 4:
                self.timeLastCommand = time.time()
                self.describe(self.chatroom, "perks his head up")
        elif search(r"(^|\s)+good boy!*(\s|$)+", message, IGNORECASE):
            timeRightNow = time.time()
            if (timeRightNow - self.timeLastCommand) > 4:
                self.timeLastCommand = time.time()
                self.describe(self.chatroom, "barks")
        elif (search(r"(^|\s)+wow!*(\s|$)+", message, IGNORECASE) or
        search(r"(^|\s)+very(\s|$)+", message, IGNORECASE) or
        search(r"(^|\s)+such(\s|$)+", message, IGNORECASE)):
            timeRightNow = time.time()
            if (timeRightNow - self.timeLastCommand) > 4:
                self.timeLastCommand = time.time()
                self.msg(self.chatroom, "Wow!")


def main():
    f = protocol.ReconnectingClientFactory()
    f.protocol = Doge

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()


if __name__ == "__main__":
    main()
