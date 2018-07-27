#!/usr/bin/python2.7

import time
import random
import re
import datetime
from lxml import html
import requests

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, defer
import string

serv_ip = "coop.test.adtran.com"
serv_port = 6667
channel = "#main"

try:
    with open("../admin_ip.txt", "r") as infile:
        admin_ip = infile.readline().strip()
except (IOError):
    admin_ip = ""
finally:
    if admin_ip != "":
        print("Admin IP: " + admin_ip)
    else:
        print("WARNING: No Admin IP recognized")

class memeBot(irc.IRCClient):
    nickname = "MemeBot"

    def signedOn(self):
        self.join(channel)
        self.user_list = []
        self.__last_response = 0
        self.__last_murica = 0
        self.__ignore = []
        self.__channel = channel
        print("Channel: " + self.__channel)
        self.who(channel)
        self.memelist = []

        with open("ignore_list.txt", 'r') as infile:
            for each in infile:
                self.__ignore.append(each.strip())
        print("Ignore list", self.__ignore)

    def luserClient(self, info):
        print(info)

    def userJoined(self, user, channel):
        print("JOINED:", channel, user)
        self.who(channel)

    def userLeft(self, user, channel):
        print("LEFT:", channel, user)
        self.who(channel)

    def userQuit(self, user, quitMessage):
        print("QUIT:", user)
        self.who(channel)

    def userRenamed(self, oldname, newname):
        print(oldname, "is now known as", newname.lower())
        self.who(channel)

    def who(self, channel):
        "List the users in 'channel', usage: client.who('#some-room')"
        self.user_list = []
        self.sendLine('WHO %s' % channel)

    def irc_RPL_WHOREPLY(self, *nargs):
        "Receive WHO reply from server"
        usr = {}
        usr["nick"] = nargs[1][5]
        usr["host"] = nargs[1][2]
        usr["ip"] = nargs[1][3]
        self.user_list.append(usr)

    def irc_RPL_ENDOFWHO(self, *nargs):
        "Called when WHO output is complete"
        print "Users:"
        for each in self.user_list:
            print each["nick"],
        print
        return

    def irc_unknown(self, prefix, command, params):
        '''
        "Print all unhandled replies, for debugging."
        print 'UNKNOWN:', prefix, command, params
        '''
        return

    def ignore(self, nick):
        # look up user in room list
        for each in self.user_list:
            if each["nick"] == nick:
                host = each["host"]
                break

        if host not in self.__ignore:
            # add host to ignore list
            self.msg(self.__channel, "Now ignoring %s" % nick)
            self.__ignore.append(host)
            print "Ignore list", self.__ignore
            with open("ignore_list.txt", "w") as ofile:
                for each in self.__ignore:
                    ofile.write(each + "\n")
        return

    def unignore(self, nick):
        # look up user in room list
        for each in self.user_list:
            if each["nick"] == nick:
                host = each["host"]
                break

        if host in self.__ignore:
            # remove host from ignore list
            self.msg(self.__channel,
                    "Oh hi %s. How long have you been here?" % nick)
            self.__ignore.remove(host)
            print "Ignore list", self.__ignore
            with open("ignore_list.txt", "w") as ofile:
                for each in self.__ignore:
                    ofile.write(each + "\n")
        return

    def ignore_list(self):
        msg = ""
        for i in range(len(self.user_list)):
            if self.user_list[i]["host"] in self.__ignore:
                msg += self.user_list[i]["nick"] + " "
        self.msg(channel, "Ignore list: " + msg)

    def get_memes(self):
        page = requests.get("https://www.reddit.com/r/memes/")
        if page.ok:
            self.memelist = []
            tree = html.fromstring(page.content)
            links = tree.find_class("title")
            for each in links:
                href = each.get("href")
                if href != None:
                    if "/r/memes/" in href:
                        self.memelist.append("https://www.reddit.com" + href)
                    else:
                        self.memelist.append(href)
        page.close()
        print page.ok

    def pick_meme(self):
        print random.choice(self.memelist)

    def murica(self, channel, host, temp_time):
        try:
            with open("muricans.txt", "r") as infile:
                muricans = []
                for each in infile:
                    muricans.append(each.strip())
                if host in muricans:
                    stars1 = "\x0316,2* * * * * *"
                    stars2 = "\x0316,2 * * * * * "
                    stripe1 = "\x034,4                   ,"
                    stripe2 = "\x0316,16                   ,"
                    stripe3 = "\x034,4                              ,"
                    stripe4 = "\x0316,16                              ,"
                    for i in range(4):
                        self.msg(channel, stars1 + stripe1)
                        self.msg(channel, stars2 + stripe2)
                    self.msg(channel, stars1 + stripe1)
                    for i in range(2):
                        self.msg(channel, stripe4)
                        self.msg(channel, stripe3)
                    self.__last_murica = temp_time
                    return
        except (IOError):
            print "ERROR: muricans.txt not found"

    def admin_cmds(self, channel, message):
        # if message == "get_memes":
        #     self.get_memes()
        # elif message == "pick_meme":
        #     self.pick_meme()

        m = re.match(self.nickname + r",*\s(\w+) (.*)", message)
        if m:
            if m.group(1) == "ignore":
                self.ignore(m.group(2).strip())
                return

            elif m.group(1) == "unignore":
                self.unignore(m.group(2).strip())
                return

            elif m.group(1) == "say":
                self.msg(self.__channel, m.group(2))
                return

            '''
            elif m.group(1) == "list":
                print "DEBUG"
                self.ignore_list()
                return
            '''

    def rip(self, channel, temp_time):
        responses = ["rip", "ripperonie", "merry RIP-mas", "ripripripriprip", "RIP", "f", "F"]
        self.msg(channel, random.choice(responses))
        self.__last_response = temp_time


    def doot(self, channel, message, temp_time):
        numDoots = message.count("doot")
        if numDoots > 70:
            responses = ["...no", "ano", "BOI", "stahp", "Bruh chill"]
            self.msg(channel, random.choice(responses))
            return
        self.describe(channel, "doot " + "doot " * numDoots)
        self.__last_response = temp_time

    def achoo(self, channel, temp_time, user_name):
        responses = ["bless you %s", "hands %s a tissue"]
        self.describe(channel, random.choice(responses) % user_name)
        self.__last_response = temp_time

    def hr(self, channel, temp_time):
        responses = ["HR", "BECKY", "MEGAN", "HR HR HR HR", "HUMAN RESOURCES"]
        self.msg(channel, random.choice(responses))
        self.__last_response = temp_time


    def de_way(self, channel, temp_time):
        responses = ["Sho me de wey", "Dat is not de wey",\
                     "DIS IS DE WEY", "Where is our queen?",\
                     "R u duh queen?"]
        chance = random.randint(1,100)
        if chance <= 75:
            self.msg(channel, random.choice(responses))
        else:
            chance = random.randint(1,100)
            if chance <= 50:
                self.describe(channel, "cluck " * random.randint(1,20))
            else:
                self.describe(channel, "bwah " * random.randint(1,20))
        self.__last_response = temp_time

    def have_a_nice_day(self, channel, temp_time, message):
        m = re.match(r"(.*have\sa\s(very\s)*(nice\s)*day.*)", message.lower())
        if m.group(3) != None:
            numVery = message.count("very")
            if numVery > 60:
                responses = ["Have a day :^)"]
                self.msg(channel, random.choice(responses))
                return
            self.msg(channel, "Have a very " + ("very " * numVery) + "nice day")
            self.__last_response = temp_time
        else:
            responses = ["Thanks, you too :^)"]
            self.msg(channel, random.choice(responses))
            self.__last_response = temp_time


    def hump_day(self, channel, temp_time):
        responses = ["HUMP DAAAAYYYYYYYYYYYY", "MIKE MIKE MIKE MIKE MIKE MIKE MIKE MIKE"]
        self.msg(channel, random.choice(responses))
        self.__last_response = temp_time

    def clark(self, channel, temp_time, host):
        try:
            with open("disciples.txt", "r") as infile:
                disciples = []
                for each in infile:
                    disciples.append(each.strip())
                if host in disciples:
                    responses = ["amen", "f", "praise"]
                    self.msg(channel, random.choice(responses))
                    self.__last_response = temp_time
                else:
                    self.rip(channel, temp_time)

        except (IOError):
            print "ERROR: disciples.txt not found"

    def odds(self, channel, temp_time):
        reactor.callLater(0, self.msg, channel, "3")
        reactor.callLater(1, self.msg, channel, "2")
        reactor.callLater(2, self.msg, channel, "1")
        reactor.callLater(3, self.msg, channel, "GO!")
        temp_time = time.time()
        return 

    def oof_owie(self, channel, temp_time):
        self.msg(channel, "owie")
        self.__last_response = temp_time

    def help_message(self, channel):
        msg = "Hi! I'm memeBot!  I don't "
        self.msg(channel, msg)
        return

    def privmsg(self, user, channel, message):
        user_name = user.split("!")[0]
        user_ip = user.split("@")[1]
        host = re.match(r"\w+!(~\w+)@", user).group(1)
        temp_time = time.time()

        # pm privilages
        if (channel == self.nickname) and user_ip != admin_ip:
            return

        # print(channel, user, message)
        if (temp_time - self.__last_response > 5) or user.split("@")[1] == admin_ip:
            # admin commands
            if user_ip == admin_ip:
                self.admin_cmds(channel, message)

            # ignore list
            if host in self.__ignore:
                return

            # murica
            elif message == "murica"\
              and (temp_time - self.__last_murica > 30):
                self.murica(channel, host, temp_time)

            # match rip
            elif re.search(r"(\brip\b)", message.lower()):
                self.rip(channel, temp_time)

            # doot doot
            elif re.search(r"(\bdoot\b)", message.lower()):
                self.doot(channel, message.lower(), temp_time)

            # achoo
            elif re.search(r"(\bachoo\b|\bsneeze\b|\basneeze\b)", message.lower()):
                self.achoo(channel, temp_time, user_name)

            # :hr:
            elif re.search(r"(\b\:hr\:\b|\bhr\b)", message.lower()):
                self.hr(channel, temp_time)

            # show me de way
            elif re.search(r"(\bwey\?*\.*\:*\b)", message.lower()):
                self.de_way(channel, temp_time)

            # have a nice day
            elif re.search(r"(have\sa\s(very\s)*(nice\s)*day)", message.lower()):
                self.have_a_nice_day(channel, temp_time, message)

            # hump day
            elif re.search(r"what\sday\sis\sit(/stoday)*\?*", message.lower())\
              and datetime.date.today().weekday() == 2:
                self.hump_day(channel, temp_time)

            # praise clark in the ark
            elif re.search(r"praise\sclark\s(in\sthe\s|and\shis\s)ark|\bf\b", message.lower()):
                self.clark(channel, temp_time, host)

            # odds
            elif re.search(self.nickname + r",*\sodds", message):
                self.odds(channel, temp_time)

            # oof owie
            elif re.search(r"\boof\b|\b:oof:\b", message.lower()):
                self.oof_owie(channel, temp_time)

            # general business
            #TODO

            else:
                return




def main():
    f = protocol.ClientFactory()
    f.protocol = memeBot

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()


if __name__ == "__main__":
    main()

'''
TODO
FEATURES
general business
    - <jlong> like "we should classify this as general business" -> Memebot /me salutes or -> "Ah yes, General Business"

r/memes
    - look at conch's pokemon thing
'''
