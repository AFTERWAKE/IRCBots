#!/usr/bin/python2.7

import random
import re
import json

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from lxml import html
import requests

from twisted.internet import defer

serv_ip = "coop.test.adtran.com"
serv_port = 6667
channel = "#main"

with open(r'Magic_Conch.json') as f:
    config = json.load(f)

try:
    with open(r'../admin_ip.txt', 'r') as infile:
        admin_ip = infile.readline().strip()
except (IOError):
    admin_ip = ''
finally:
    if admin_ip != '':
        print("Admin IP:", admin_ip)
    else:
        print("WARNING: No admin IP recognized")

class theMagicConch(irc.IRCClient):
    nickname = config["nick"]

    def signedOn(self):
        self.join(channel)
        self.pokemon_list = self.get_pokemon()
        self.user_list = []
        self.__ignore = []
        self.__channel = channel
        print("Channel: " + self.__channel)
        print("Nick: " + self.nickname)

        with open("ignore_list.txt", 'r') as infile:
            for each in infile:
                self.__ignore.append(each.strip())
        print("Ignore list", self.__ignore)

        # print(self.msg("NAMES %s" % config["channel"]))  #idk what this was
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

            '''
            elif m.group(1) == "list":
                print "DEBUG"
                self.ignore_list()
                return
            '''

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

    def STALEprivmsg(self, user, channel, message):
        # print(channel, user + ":", message)
        user_ip = user.split("@")[1]
        host = re.match(r"\w+!(~\w+)@", user).group(1)
        user = user.split('!')[0]

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

        # bypass pms
        if channel != self.__channel:
            return

        # ignore list
        if host in self.__ignore:
            return

        # triggers

    def privmsg(self, user, channel, message):
        user_name = user.split("!")[0]
        user_ip = user.split("@")[1]
        host = re.match(r"\w+!(~\w+)@", user).group(1)
        temp_time = time.time()

        # pm privilages
        if (channel == self.nickname) and user_ip != admin_ip:
            return

        # admin commands
        if user_ip == admin_ip:
            self.admin_cmds(channel, message)

        # ignore list
        if host in self.__ignore:
            return

        # Triggers
        # Pokemon
        if re.search(r"Magic[ _]Conch,.*which\spokemon.*\?", message):
            msg = random.choice(["%s",
                                 "I choose %s!",
                                 "I think it was %s...",
                                 "I believe it was %s",
                                 "definitely %s!",
                                 "absolutely %s!",
                                 "not %s",
                                 "definitely not %s"])

            # choose random pokemon
            pokemon = random.choice(self.pokemon_list)

            # append link to pokemon
            msg += " " + pokemon["link"]

            # send message with pokemon's name inserted
            self.msg(channel, msg % pokemon["name"])
            return

            else:
                self.msg(channel, msg)
                return

            self.msg(channel, msg)
            return

        # who
        elif re.search(r"Magic[ _]Conch,.*who.*", message):
            msg = random.choice(["%s",
                                 "I think it was %s...",
                                 "I believe it was %s",
                                 "definitely %s!",
                                 "absolutely %s!"])

            msg = msg % random.choice(self.user_list)["nick"]
            self.msg(channel, msg)
            return

        # how much/many
        elif re.search(r"Magic[ _]Conch,.*\s*how\s(many|many).*\?", message):
            msg = [ random.randint(0,20),
                    "A lot",
                    "Some",
                    "Not many",
                    "Few",
                    "None",
                    "All of them",
                    "More than you'd expect"]
            self.msg(channel, msg)

        # where
        elif re.search(r"Magic[ _]Conch,.*\s+where\s+.*\?", message):
            msg = "Follow the seahorse"
            self.msg(channel, msg)

        else:
            return


    def get_pokemon(self):
        page = requests.get("https://pokemondb.net/pokedex/national")
        tree = html.fromstring(page.content)
        pokemon_list = tree.find_class("ent-name")
        for i in range(len(pokemon_list)):
            mon = {"name":pokemon_list[i].text_content(),
                   "link":"https://pokemondb.net" + pokemon_list[i].attrib["href"]}
            pokemon_list[i] = mon
        page.close()
        return pokemon_list

def main():
    f = protocol.ClientFactory()
    f.protocol = theMagicConch

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()


if __name__ == "__main__":
    main()

'''
TODO:
'''
