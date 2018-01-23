import time
import random
import re

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
import enchant
import string


serv_ip = "coop.test.adtran.com"
serv_port = 6667
channel = "#main"

class blessYouBot(irc.IRCClient):
    nickname = "DootBot"

    def signedOn(self):
        self.join(channel)
        self.__d = enchant.Dict("en_US")
        self.__ex = set(string.punctuation)
        self.__user_list = []
        self.__last_response = 0

        with open("acronyms.txt", 'r') as infile:
            for each in infile:
                self.__d.add(each)

        with open("custom_words.txt", 'r') as infile:
            for each in infile:
                self.__d.add(each)

        with open("bot_list.txt", 'r') as infile:
            for each in infile:
                self.__d.add(each)

        self.__user_list = []

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
        temp_time = time.time()
        user = user.split('!')[0]
        if user not in self.__user_list:
            self.__user_list.append(user.lower())

        print(channel, user, message)
        if (temp_time - self.__last_response > 5):
            for word in message.split():
                # strip punctuations and lowercase word
                word = ''.join(ch for ch in word if ch not in self.__ex).lower()
                if word == "":
                    pass

                # match rip
                elif re.match(r".*rip.*", message.lower()):
                    responses = ["rip", "ripperonie", "merry RIP-mas", "ripripripriprip"]
                    self.msg(channel, random.choice(responses))
                    self.__last_response = temp_time
                    return

                # doot doot
                elif re.match(r"doot", message.lower()):
                    self.describe(channel, "doot doot")
                    self.__last_response = temp_time
                    return

                # achoo
                elif re.match(r"achoo", message.lower()):
                    responses = ["bless you %s", "hands %s a tissue"]
                    self.describe(channel, random.choice(responses) % user)
                    self.__last_response = temp_time
                    return

                # :hr:
                elif re.match(r".*:hr:.*", message.lower()):
                    responses = ["HR"]
                    self.msg(channel, random.choice(responses))
                    self.__last_response = temp_time

                # # bless you
                # elif not self.__d.check(word):
                #     chance = random.randint(1,100)
                #     print("CATCH:", word, "chance: " + str(chance))
                #     responses = ["bless you %s", "hands %s a tissue"]
                #     if (chance <= 20):
                #         self.describe(channel, random.choice(responses) % user)
                #         self.__last_response = temp_time
                #     return

                else:
                    return




def main():
    f = protocol.ClientFactory()
    f.protocol = blessYouBot

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()


if __name__ == "__main__":
    main()

'''
TODO
- fix "rip" regex
- think of a way for the bot to dynamically update word list so that I don't have to update it every time
    ooh or make a master command
- implement so that the bot understands I'm the master
    *note: look at how noah did it in theCount
- recognize multiple doots
'''
