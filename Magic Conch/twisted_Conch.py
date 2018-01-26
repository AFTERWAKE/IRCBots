import random
import re
import json

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from lxml import html
import requests

from twisted.internet import defer

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
        self.join(config["channel"])
        self.pokemon_list = self.get_pokemon()
        self._namescallback = {}
        self.__ignore = []
        self.__channel = config["channel"]
        print("Channel: " + self.__channel)

        with open("ignore_list.txt", 'r') as infile:
            for each in infile:
                self.__ignore.append(each.strip())
        print("Ignore list", self.__ignore)

        # print(self.msg("NAMES %s" % config["channel"]))  #idk what this was
           
    def luserClient(self, info):
        print(info)

    def userJoined(self, user, channel):
        print("JOINED:", channel, user)

    def userLeft(self, user, channel):
        print("LEFT:", channel, user)
    
    def userQuit(self, user, quitMessage):
        print("QUIT:", user)

    def userRenamed(self, oldname, newname):
        print(oldname, "is now known as", newname)

    def privmsg(self, user, channel, message):
        print(channel, user + ":", message)
        # bypass pms
        if channel == config["nick"]:
            return
        user_ip = user.split("@")[1]
        host = re.match(r"\w+!~(\w+)@", user).group(1)
        user = user.split('!')[0]

        # admin commands
        if user_ip == admin_ip:
            m = re.match(self.nickname + r",*\s(\w+) (\w+)", message)
            if m:
                if m.group(1) == "ignore":
                    if m.group(2) not in self.__ignore:
                        self.msg(self.__channel, "Now ignoring %s" % m.group(2))
                        self.__ignore.append(m.group(2))
                        print("Ignore list", self.__ignore)
                        with open("ignore_list.txt", "w") as ofile:
                            for each in self.__ignore:
                                ofile.write(each + "\n")
                        return

                elif m.group(1) == "unignore":
                    if m.group(2) in self.__ignore:
                        self.msg(self.__channel, 
                                "Oh hi %s. How long have you been here?" % m.group(2))
                        self.__ignore.remove(m.group(2))
                        print("Ignore list", self.__ignore)
                        with open("ignore_list.txt", "w") as ofile:
                            for each in self.__ignore:
                                ofile.write(each + "\n")
                        return

                elif m.group(1) == "say":
                    self.msg(self.__channel, message)
                    return


        # ignore list
        if host in self.__ignore:
            '''
            chance = random.randint(1,100)
            if chance <= 10:
                self.msg(channel, random.choice(["I don't know what that means"]))
            '''
            return

        for trigger in config["triggers"]:
            for expression in trigger["message"]:
                if re.match(expression, message):
                    response = random.choice(trigger["responses"])
                    '''
                    if re.match(r"who:*(\w*)", response):
                        m = re.match(r"who:*(\w*)", response)

                        # allow users to input custom conch messages
                        m = re.match(r"who:*(.*)", response)
                        if m.group(1) == "":
                            msg = "I choose %s!"
                        else:
                            msg = m.group(1)

                        msg = msg % random.choice(["dummy_name"])
                        self.msg(channel, msg)
                        return

                    elif re.match(r"pokemon:*(.*)", response):
                        m = re.match(r"pokemon:*(.*)", response)
                        if m.group(1) == "":
                            msg = "I choose %s!"
                        else:
                            msg = m.group(1)

                        # choose random pokemon
                        pokemon = random.choice(self.pokemon_list)

                        # append link to pokemon 
                        msg += " " + pokemon["link"]

                        # send message with pokemon's name inserted
                        self.msg(channel, msg % pokemon["name"])
                        return

                    else:
                        self.msg(channel, response)
                        return
                    '''
                    self.msg(channel, response)
                    return


    def names(self, channel):
        channel = channel.lower()
        d = defer.Deferred()
        if channel not in self._namescallback:
            self._namescallback[channel] = ([], [])

        self._namescallback[channel][0].append(d)
        self.sendLine("NAMES %s" % channel)
        return d

    def irc_RPL_NAMREPLY(self, prefix, params):
        channel = params[2].lower()
        nicklist = params[3].split(' ')

        if channel not in self._namescallback:
            return

        n = self._namescallback[channel][1]
        n += nicklist

    def irc_RPL_ENDOFNAMES(self, prefix, params):
        channel = params[1].lower()
        if channel not in self._namescallback:
            return

        callbacks, namelist = self._namescallback[channel]

        for cb in callbacks:
            cb.callback(namelist)

        del self._namescallback[channel]

    def update_room_list(self):
        print(defer.gatherResults(self.names(config["channel"])))

    def populate(self, nicklist):
        for each in nicklist:
            print(each)
    
    def get_pokemon(self):
        page = requests.get("https://pokemondb.net/pokedex/national")
        tree = html.fromstring(page.content)
        pokemon_list = tree.find_class("ent-name")
        for i in range(len(pokemon_list)):
            mon = {"name":pokemon_list[i].text_content(),
                   "link":"https://pokemondb.net" + pokemon_list[i].attrib["href"]}
            pokemon_list[i] = mon
        return pokemon_list

def main():
    serv_ip = "coop.test.adtran.com"
    serv_port = 6667

    f = protocol.ClientFactory()
    f.protocol = theMagicConch

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()


if __name__ == "__main__":
    main()

'''
TODO:
    - throttle
    - fix who
'''
