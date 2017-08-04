import time
import random
import re

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
import enchant
import string


serv_ip = "coop.test.adtran.com"
serv_port = 6667
channel = "#test"

class blessYouBot(irc.IRCClient):
    nickname = "blessYouBot"

    def signedOn(self):
        self.join(channel)
        self.__d = enchant.Dict("en_US")
        self.__ex = set(string.punctuation)

        self.__acronyms = []
        with open(acronyms.txt, 'r') as infile:
            for each in infile:
                self.__acronyms.append(each)

        self.__custom_words = []
        with open(custom_words.txt, 'r') as infile:
            for each in infile:
                self.__custom_words.append(each)

        self.__bot_list = []
        with open(bot_list.txt, 'r') as infile:
            for each in infile:
                self.__bot_list.append(each)

        self.__user_list = []

        print("acronyms:", self.__acronyms)
        print("custom_words:", self.__custom_words)
        print("bots:", self.__bot_list)
           
    def luserClient(self, info):
        print(info)

    def userJoined(self, user, channel):
        print("JOINED:", channel, user)
        if user not in self.__user_list:
            self.__user_list.append(user.lower())

    def userLeft(self, user, channel):
        print("LEFT:", channel, user)
        if user in self.__user_list:
            self.__user_list.remove(user.lower())
   
    def userQuit(self, user, quitMessage):
        print("QUIT:", user)
        if user in self.__user_list:
            self.__user_list.remove(user.lower())

    def userRenamed(self, oldname, newname):
        print(oldname, "is now known as", newname.lower())
        if oldname in self.__user_list:
            self.__user_list.remove(oldname.lower())

        if newname not in self.__user_list:
            self.__user_list.append(user.lower())

    def privmsg(self, user, channel, message):
        user = user.split('!')[0]
        if user not in self.__user_list:
            self.__user_list.append(user.lower())
        print(channel, user + ":", message)
        for word in message.split():
            # ignore bots
            if user in self.__bot_list:
                return

            # strip punctuations and lowercase word
            word = ''.join(ch for ch in word if ch not in self.__ex).lower()
            if word == "":
                pass

            # ignore user's names
            if word in self.__user_list:
                pass

            # accomodate for acronyms and non US words
            elif word in self.__acronyms or word in self.__custom_words:
                pass

            # match rip
            elif re.match(r".*rip.*", message.lower()):
                responses = ["rip", "ripperonie", "merry RIP-mas", "ripripripriprip"]
                self.msg(channel, random.choice(responses))
                return

            # bless you
            elif not self.__d.check(word):
                print("CATCH:", word)
                responses = ["bless you %s", "/me hands %s a tissue"]
                self.msg(channel, random.choice(responses) % user)
                return

            else:
                return
            



def main():
    f = protocol.ClientFactory()
    f.protocol = blessYouBot

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()


if __name__ == "__main__":
    main()
