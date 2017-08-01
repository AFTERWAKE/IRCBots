#!python3
__author__ = 'mhill'

#!python3
import socket
import random
import time
import re
import json
import requests
from lxml import html


class Bot:
    def __init__(self, server, channel, nick, ident):
        self.server = server
        self.channel = channel
        self.nick = nick
        self.triggers = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((server, 6667))
        self.sock.recv(2048)
        self.sock.send(("USER " + nick + " " + nick + " " + nick + " : " + ident + "\r\n").encode('utf-8'))
        self.sock.send(("NICK " + nick + "\r\n").encode('utf-8'))
        time.sleep(2)
        if nick.upper() == "MAGIC_CONCH":
            self.pokemon_list = get_pokemon()

    def sendmsg(self, chan, msg):
        self.send("PRIVMSG " + chan + " :" + msg + "\r\n")

    def joinchan(self, chan):
        self.send("JOIN " + chan + "\r\n")

    def send(self, msg):
        self.sock.send(msg.encode('utf-8'))

    def recv(self, amount):
        return self.sock.recv(amount).decode('utf-8')

    def action(self, chan, action):
        self.sendmsg(chan, '\x01ACTION ' + action + '\x01')

    def add_trigger(self, trigger):
        self.triggers.append(trigger)

    def users(self):
        #^:(?P<nick>\w+)!~(?P<real>[\w @\.]+)\s*PRIVMSG\s*#(?P<channel>\w+)\s*:ACTION(?P<message>.*)$
        pass
    
    def act(self):
        while True:
            ircmsg = self.recv(2048).strip('\n\r')
            print(ircmsg)
            if ircmsg.find("PING :") != -1:
                pingid = ircmsg.split(':')
                self.send("PONG " + pingid[-1] + "\r\n")
            elif ircmsg.find("IRC.SERVER NOTICE " + self.nick + " :on ") != -1:
                self.joinchan(self.channel)
            else:
                for item in self.triggers:
                    if item.attempt(ircmsg):
                        print(item.get_response())
                        if item.command:
                            if item.get_response() == 'quit':
                                self.sock.close()
                                return
                        if item.action:
                            self.action(self.channel, item.get_response())
                            break

                        # Choose someone random in the channel
                        if re.match(r"who:*(\w*)", item.get_response()):
                            # look for a response of "who" and get a list of all in the channel
                            msg = "NAMES %s \r\n" % (self.channel)
                            self.send(msg)
                            names = self.recv(2048).strip('\n\r')
                            names = re.match(r".*:(.*)", names)[1].split()

                            # allow users to input custom conch messages
                            m = re.match(r"who:*(.*)", item.get_response())
                            if m[1] == "":
                                msg = "I choose %s!"
                            else:
                                msg = m[1]
                            msg = msg % random.choice(names)
                            self.sendmsg(self.channel, msg)
                            break
                            
                        # Choose a random pokemon from pokemondb.net
                        if re.match(r"pokemon:*(\w*)", item.get_response()):
                            m = re.match(r"pokemon:*(.*)", item.get_response())
                            if m[1] == "":
                                msg = "I choose %s!"
                            else:
                                msg = m[1]

                            # choose random pokemon
                            pokemon = random.choice(self.pokemon_list)

                            # append link to pokemon 
                            msg += " " + pokemon["link"]

                            # send message with pokemon's name inserted
                            self.sendmsg(self.channel, msg % pokemon["name"])
                            break

                        else:
                            self.sendmsg(self.channel, item.get_response())
                            break


class Trigger:
    def __init__(self, pattern, responses, isAction, isCommand, *args):
        self.regex = re.compile(pattern, re.I)
        self.action = isAction
        self.responses = responses
        self.groups = args
        self.command = isCommand

    def attempt(self, message):
        match = self.regex.match(message)
        if match and len(self.groups) > 0:
            for group in self.groups:
                if not group.match(match.group(group.name)):
                    return False
            return True
        elif match:
            return True
        return False

    def get_response(self):
        return random.choice(self.responses)


class Group:
    def __init__(self, group, *args):
        self.name = group
        self.allow = [re.compile(x, re.I) for x in args]

    def match(self, string):
        for item in self.allow:
            if item.match(string):
                return True
        return False

def get_pokemon():
    page = requests.get("https://pokemondb.net/pokedex/national")
    tree = html.fromstring(page.content)
    pokemon_list = tree.find_class("ent-name")
    for i in range(len(pokemon_list)):
        mon = {"name":pokemon_list[i].text_content(),
               "link":"https://pokemondb.net" + pokemon_list[i].attrib["href"]}
        pokemon_list[i] = mon
    return pokemon_list

