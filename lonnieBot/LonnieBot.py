#!/usr/bin/python2.7
r"""

    @Author: Jacob Blair
    @date: January 2020
    @file: LonnieBot.py

"""
import random
import re
import datetime
import exceptions
import time
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, task

serv_ip = ""
serv_port = 6667
channel = ""

with open("laws.txt.", 'r') as lawsFile:
    laws = [str(line) for line in lawsFile]

try:
    admin_ip = ""
finally:
    if admin_ip != "":
        print("Admin IP: " + admin_ip)
    else:
        print("WARNING: No Admin IP recognized")


class lonnieBot(irc.IRCClient):
    nickname = "Lonnie"

    def __init__(self):
        self.wisdom = False
        self.wisdomQueued = False
        lc = task.LoopingCall(self.scheduleEvents)
        lc.start(60)

    def signedOn(self):
        self.join(channel)
        self.user_list = []
        self.__last_response = 0
        self.__ignore = []
        self.__channel = channel
        print("Channel: " + self.__channel)
        self.who(channel)

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

    def scheduleEvents(self):
        if self.wisdomQueued:
            self.wisdomQueued = False
            self.autoWisdom()
            return
        now = datetime.datetime.time(datetime.datetime.now())
        morninglaw = datetime.time(hour=8, minute=59)
        afternoonlaw = datetime.time(hour=13, minute=59)

        if now.hour == morninglaw.hour and now.minute == morninglaw.minute:
            self.autoWisdom()
        elif now.hour == afternoonlaw.hour and now.minute == afternoonlaw.minute:
            self.autoWisdom()

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

    def admin_cmds(self, channel, message):
     
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


    def spoutWisdom(self, channel, temp_time):
        self.msg(channel, random.choice(laws))
        self.__last_response = temp_time

    def autoWisdom(self):
        if self.wisdom:
            self.wisdomQueued = True
            return
        self.msg(channel, random.choice(laws))
        
    def genBusiness(self, channel, temp_time):
        responses = ["Ah yes. General Business", "The generalist of businesses", "Tom would be proud of your work ethic"]
        self.msg(channel, random.choice(responses))
        self.__last_response = temp_time

    def helpText(self, channel, temp_time):
        self.msg(channel, "Hi Everyone. I automatically say one of Lonnie\'s laws at about 9 A.M. and 2 P.M."
                            + "However, if you would like to hear a law to better your day with some of Lonnie\'s profound wisdom, just say \"lonnie, law\" (With or without the comma i/m not picky)")
        self.__last_response = temp_time

    def privmsg(self, user, channel, message):
        user_name = user.split("!")[0]
        user_ip = user.split("@")[1]
        msg = message.split()

        try:
            host = re.match(r"\w+!~(\w+)@", user).group(1)
        except exceptions.AttributeError:
            host = ""
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


            # match spoutWisdom
            elif re.search(r'lonnie..l.w', message.lower()):
                self.spoutWisdom(channel, temp_time)

            elif re.search(r'lonnie..h..p', message.lower()):
                self.helpText(channel, temp_time)

            elif re.search("business", message.lower()):
                self.genBusiness(channel, temp_time)

            else:
                return


def main():
    f = protocol.ClientFactory()
    f.protocol = lonnieBot

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()


if __name__ == "__main__":
    main()

