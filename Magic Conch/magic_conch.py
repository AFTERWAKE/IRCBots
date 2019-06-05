#!/usr/bin/python2.7

import random
import re
import json
import os.path

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from lxml import html
import requests

from twisted.internet import defer

serv_ip = "coop.test.adtran.com"
serv_port = 6667
channel = "#main"

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
    nickname = "Magic_Conch"

    def signedOn(self):
        self.join(channel)
        self.pokemon_list = self.get_pokemon()
        self.user_list = []
        self.__ignore = []
        self.__channel = channel
        print("Channel: " + self.__channel)
        print("Nick: " + self.nickname)

        if not os.path.exists("ignore_list.txt"):
            print "ignore_list.txt not found, creating an empty one..."
            open("ignore_list.txt", 'w').close()

        with open("ignore_list.txt", 'r') as infile:
            for each in infile:
                self.__ignore.append(each.strip())
        print("Ignore list", self.__ignore)

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

    def privmsg(self, user, channel, message):
        user_name = user.split("!")[0]
        user_ip = user.split("@")[1]
        host = re.match(r"\w+!(~\w+)@", user).group(1)

        # pm privilages
        if (channel == self.nickname) and user_ip != admin_ip:
            return

        # admin commands
        if user_ip == admin_ip and not re.search(r"\?", message):
            self.admin_cmds(channel, message)
            return

        # ignore list
        if host in self.__ignore:
            return

        # Triggers
        # Pokemon
        if re.search(self.nickname + r".*which\spokemon.*\?", message):
            msg = random.choice(["%s",
                                 "I choose %s!",
                                 "I think it was %s...",
                                 "I believe it was %s",
                                 "definitely %s!",
                                 "absolutely %s!"])

            # choose random pokemon
            pokemon = random.choice(self.pokemon_list)

            # append link to pokemon
            msg += " " + pokemon["link"]

            # send message with pokemon's name inserted
            self.msg(channel, msg % pokemon["name"])
            return

            self.msg(channel, msg)
            return

        # who
        elif re.search(r"Magic[ _]Conch.*who.*", message):
            msg = random.choice(["%s",
                                 "I think it was %s...",
                                 "I believe it was %s",
                                 "definitely %s!",
                                 "absolutely %s!"])

            msg = msg % random.choice(self.user_list)["nick"]
            self.msg(channel, msg)
            return

        # how much/many
        elif re.search(r"Magic[ _]Conch.*\s*how\s(much|many).*\?", message):
            msg = random.choice([ str(random.randint(0,20)),
                                  "A lot",
                                  "Some",
                                  "Not many",
                                  "Few",
                                  "None",
                                  "All of them",
                                  "More than you'd expect"])
            self.msg(channel, msg)

        # where
        elif re.search(r"Magic[ _]Conch.*\s*where\s*.*\?", message):
            msg = "Follow the seahorse"
            self.msg(channel, msg)

        # or
        elif re.search(r"Magic[ _]Conch.*\s+or\s+.*\?", message):
            msg = random.choice(["Neither",
                                 "Both",
                                 "The first one.",
                                 "The second one."])
            self.msg(channel, msg)

        # what do
        elif re.search(r"Magic[ _]Conch.*what\sdo.*\\?", message):
            msg = random.choice(["Nothing.",
                                 "Everything.",
                                 "Very little.",
                                 "Very much.",
                                 "All the things."])
            self.msg(channel, msg)

        # what is love
        elif re.search(r"Magic[ _]Conch.*what\s*is\s*love.*\?.", message):
            msg = "Baby don't hurt me, don't hurt me, no more~"
            self.msg(channel, msg)

        # generic response
        elif re.search(r"Magic[ _]Conch.*\?", message):
            msg = random.choice([ "Maybe someday.",
                                  "Follow the seahorse.",
                                  "I don't think so.",
                                  "No.",
                                  "Yes.",
                                  "Try asking again.",
                                  "It is certain.",
                                  "It is decidedly so.",
                                  "Without a doubt.",
                                  "Yes definitely.",
                                  "You may rely on it.",
                                  "As I see it, yes.",
                                  "Most likely.",
                                  "Outlook good.",
                                  "Signs point to yes.",
                                  "Don't count on it.",
                                  "My sources say no.",
                                  "Outlook not so good.",
                                  "Very doubtful."])
            self.msg(channel, msg)

        # ALL HAIL THE MAGIC CONCH
        elif re.search(r"all hail the magic conch", message.lower()):
            msg = random.choice(["I am hailed!"])
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
