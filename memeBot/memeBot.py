import time
import random
import re

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
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
        self.__ignore = []
        self.__channel = channel
        print("Channel: " + self.__channel)
        self.who(channel)

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
        "List the users in 'channel', usage: client.who('#testroom')"
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

    def privmsg(self, user, channel, message):
        user_name = user.split("!")[0]
        user_ip = user.split("@")[1]
        host = re.match(r"\w+!(~\w+)@", user).group(1)
        temp_time = time.time()

        # pm privilages
        if (channel == self.nickname) and user_ip != admin_ip:
            return

        print(channel, user, message)
        if (temp_time - self.__last_response > 5) or user.split("@")[1] == admin_ip:
            # admin commands
            if user_ip == admin_ip:
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


            # ignore list
            if host in self.__ignore:
                '''
                chance = random.randint(1,100)
                if chance <= 10:
                    self.msg(channel, random.choice(["I don't know what that means"]))
                '''
                return

            # triggers/responses
            else:

                # match rip
                if re.search(r"(\brip\b)", message.lower()):
                    responses = ["rip", "ripperonie", "merry RIP-mas", "ripripripriprip", "RIP"]
                    self.msg(channel, random.choice(responses))
                    self.__last_response = temp_time
                    return

                # doot doot
                elif re.search(r"(\bdoot\b)", message.lower()):
                    numDoots = message.count("doot")
                    if numDoots > 70:
                        responses = ["...no", "ano", "BOI", "stahp", "Bruh chill"]
                        self.msg(channel, random.choice(responses))
                        return
                    self.describe(channel, "doot " + "doot " * numDoots)
                    self.__last_response = temp_time
                    return

                # achoo
                elif re.search(r"(\bachoo\b|\bsneeze\b|\basneeze\b)", message.lower()):
                    responses = ["bless you %s", "hands %s a tissue"]
                    self.describe(channel, random.choice(responses) % user_name)
                    self.__last_response = temp_time
                    return

                # :hr:
                elif re.search(r"(\b\:hr\:\b|\bhr\b)", message.lower()):
                    responses = ["HR", "BECKY", "MEGAN", "HR HR HR HR"]
                    self.msg(channel, random.choice(responses))
                    self.__last_response = temp_time
                    return

                # show me de way
                elif re.search(r"(\bwey\?*\.*\:*\b)", message.lower()):
                    responses = ["Sho me de wey", "Dat is not de wey", "DIS IS DE WEY", "Where is our queen?", "R u duh queen?"]
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
                    return

                # # ip test
                # elif re.match(r"test", message.lower()):
                #     print(user.split("@")[1], admin_ip)
                #     if user.split("@")[1] == admin_ip:
                #         self.msg(channel, user.split("!")[0] + random.choice(["is duh queen!", "knows de wey"]))
                #     else:
                #         self.msg(channel, user.split("!")[0] + random.choice(["is duh false queen!", "is not de wey", "spit on the false queen!"]))
                #     return

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
    f.protocol = memeBot

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()


if __name__ == "__main__":
    main()

'''
TODO
- add a admin mute command
- do a unmute command too
- make sure mute is done on host name
'''
