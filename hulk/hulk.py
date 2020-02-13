#!/usr/bin/python

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from re import search, IGNORECASE
from random import randint
import time
import json
import random


serv_ip = "172.22.115.228"
serv_port = 6667


class Hulk(irc.IRCClient):
    nickname = "Hulk"
    chatroom = "#testing"


    def signedOn(self):
        self.join(self.chatroom)

    def getVerb(self):
        random.seed()
        with open('verbs.txt') as json_file:
            data = json.load(json_file)
            num = random.randint(0, 632)
            return data["verbs"][num]["present"].upper()

    def privmsg(self, user, channel, message):
        if search(r"(^|\s)+smash*(\s|$)+", message, IGNORECASE):
            self.msg(self.chatroom, "3HULK " + self.getVerb() + "!!!")


def main():
    f = protocol.ReconnectingClientFactory()
    f.protocol = Hulk

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()


if __name__ == "__main__":
    main()
