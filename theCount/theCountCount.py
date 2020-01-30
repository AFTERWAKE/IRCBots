#!/usr/bin/python2.7
r"""

    @Author: Jacob Blair
    @date: January 2020
    @file: theCountCount.py

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

try:
    admin_ip = ""
finally:
    if admin_ip != "":
        print("Admin IP: " + admin_ip)
    else:
        print("WARNING: No Admin IP recognized")


class countCount(irc.IRCClient):
    nickname = "theCountCount"

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

    def remindAsked(self, channel, temp_time):
        now = datetime.datetime.time(datetime.datetime.now())
        morningCount = datetime.time(hour=8, minute=30)
        afternoonCount = datetime.time(hour=11, minute=0)
        thirdCount = datetime.time(hour=13, minute=30)
        finalCount = datetime.time(hour=16, minute=0)
        lunch = datetime.time(hour=11, minute=30)
        break_time = datetime.time(hour=15, minute=0)

        if now.hour < 8 or (now.hour == 8 and now.minute < 30):
            time = [morningCount.hour - now.hour, morningCount.minute - now.minute]
            timeMin = ((time[0] * 60) + time[1])
            timeL = [lunch.hour - now.hour, lunch.minute - now.minute]
            timeLmin = ((timeL[0] * 60) + timeL[1])
            message = "Count in " + str(timeMin) + " minutes. L.unch in " + str(timeLmin) + " minutes."
        elif now.hour >= 16 and now.minute > 2:
            time = [now.hour - morningCount.hour, now.minute - morningCount.minute]
            timeMin = ((time[0] * 60) + time[1])
            message = "Count in " + str(timeMin) + " minutes."
        elif now.hour < 11 or (now.hour == 11 and now.minute <= 1):
            time = [afternoonCount.hour - now.hour, afternoonCount.minute - now.minute]
            timeMin = ((time[0] * 60) + time[1])
            timeL = [lunch.hour - now.hour, lunch.minute - now.minute]
            timeLmin = ((timeL[0] * 60) + timeL[1])
            message = "Count in " + str(timeMin) + " minutes. L.unch in " + str(timeLmin) + " minutes."
        elif now.hour < 13 or (now.hour == 13 and now.minute < 30):
            time = [thirdCount.hour - now.hour, thirdCount.minute - now.minute]
            timeMin = ((time[0] * 60) + time[1])
            timeL = [lunch.hour - now.hour, lunch.minute - now.minute]
            timeLmin = ((timeL[0] * 60) + timeL[1])
            timeB = [break_time.hour - now.hour, break_time.minute - now.minute]
            timeBmin = ((timeB[0] * 60) + timeB[1])
            if now.hour == 11 and now.minute < 30:
                message = "Count in " + str(timeMin) + " minutes. L.unch in " + str(timeLmin) + " minutes."
            else:
                message = "Count in " + str(timeMin) + " minutes. Break in " + str(timeBmin) + " minutes."
        elif now.hour > 14 or (now.hour == 13 and now.minute > 30):
            time = [finalCount.hour - now.hour, finalCount.minute - now.minute]
            timeMin = ((time[0] * 60) + time[1])
            timeB = [break_time.hour - now.hour, break_time.minute - now.minute]
            timeBmin = ((timeB[0] * 60) + timeB[1])
            message = "Count in " + str(timeMin) + " minutes. Break in " + str(timeBmin) + " minutes."
        self.msg(channel, message)
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

            elif re.search(r'cc..time', message.lower()):
                self.remindAsked(channel, temp_time)

            else:
                return


def main():
    f = protocol.ClientFactory()
    f.protocol = countCount

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()


if __name__ == "__main__":
    main()

