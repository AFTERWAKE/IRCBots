from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, defer
from re import search, IGNORECASE
from random import sample
import time
import os

serv_ip = "coop.test.adtran.com"
serv_port = 6667

fightSongLyrics = ["I'm in the lake!!! DUN DUN DUNNNN!!!!\n",
                   "Taylor watch out for those packets! DUN DUN DUN!!!!\n",
                   "We got TA5Ks!! DUN DUN DUNNNN!!!!\n",
                   "Cable ART is on fire!! DUN DUN DUNNNN!!!\n",
                   "Calix is going down!!!! DUN DUN DUNNNN!!!\n",
                   "We got Gloria rockin at the front desk!! DUN DUN DUN!!!!!\n",
                   "Let's all go swim in the lake!! DUN DUN DUNNNN!!!\n",
                   "Dynetics WHO??!! DUN DUN DUNNNN!!!\n"]

class ChiefExecBot(irc.IRCClient):

    nickname = "tom"
    channel = "#main"
    owner = 'cn-vm-gbeagle.adtran.com'
    owner_name = ""
    currentTime = 0
    default = 'burn berNs'
    botList = [ "dad", "Seahorse", "pointbot", "botProtector","QuipBot", "MemeBot",
                "theCount", "Doge", "Calculator", "complimentBot"]
    user_list = []
    ignoreList = []


    def signedOn(self):
        self.join(self.channel)
        self.who(self.channel)

    def irc_unknown(self, prefix, command, params):
        print ("ERROR", prefix, command, params)

    def userJoined(self, user, channel):
        print (user, "has joined")
        self.who(self.channel)

    def userQuit(self, user, channel):
        print (user, "has quit")
        self.who(self.channel)

    def userRenamed(self, oldname, newname):
        print(oldname, "is now known as", newname.lower())
        self.who(self.channel)

    def who(self, channel):
        "List the users in 'channel', usage: client.who('#testroom')"
        self.user_list = []
        self.sendLine('WHO %s' % channel)

    def irc_RPL_WHOREPLY(self, *nargs):
        "Receive WHO reply from server"
        usr = {}
        finUsr = {}
        usr["nick"] = nargs[1][5]
        usr["host"] = nargs[1][2]
        usr["ip"] = nargs[1][3]

        if (usr["ip"] == self.owner):
               self.owner_name = usr["nick"]
        self.user_list.append(usr)

    def irc_RPL_ENDOFWHO(self, *nargs):
            "Called when WHO output is complete"
            print ("Users:")
            for each in self.user_list:
                print (each["nick"] + each["ip"])

    def sendmsg(self, response):
        self.currentTime = time.time()
        self.msg(self.channel, response)

    def privmsg(self, user, channel, message):
        nick = user.split('!')[0]
        user_ip = user.split('@')[1]
        user_name = []
        for name in self.user_list: user_name.append(name["nick"])

        if search(self.nickname+ r",*\shelp", message, IGNORECASE):
            self.sendmsg("ADTRAN, Inc. is a provider of telecommunications networking equipment and "
                    "internetworking products. Its headquarters are in Huntsville, Alabama.")
        elif search(r"(\bidea\b)", message, IGNORECASE):
            self.sendmsg("That's a great idea!!")

        elif search(r"(\bhackathon\b)", message, IGNORECASE):
            self.sendmsg("Woooo! Hackathon!!!!")

        elif search(r"(\badtran\b)", message, IGNORECASE):
            self.sendmsg("Goooooo ADTRAN!")

        elif search(r"(\btom\b)", message, IGNORECASE):
            self.sendmsg("It's me! Tom!!! On the eighth floor!!!!")

        elif search(r"(\bta5k\b)", message, IGNORECASE):
            self.sendmsg("You should go with the flamethrower attachment")

        elif search(r"(\bta5ks\b)", message, IGNORECASE):
            self.sendmsg("our pride and joy the TA5K")

        elif search(r"(\b(r-olt|rolt)\b)", message, IGNORECASE):
            self.sendmsg("Tomothy Remote-Optical-Line-Terminal Stanton is the name, don't wear it out ;)")

        elif search(r"(\bdynetics\b)", message, IGNORECASE):
            self.sendmsg("no cursing in adtran go wash your mouth")

        elif search(r"(\bwork\b)", message, IGNORECASE):
            self.sendmsg("werk werk werk werk werk")

        elif search(r"(\bcalix\b)", message, IGNORECASE):
            self.sendmsg("no sir")

        elif search(r"(\bworking\b)", message, IGNORECASE):
            self.sendmsg("keep working hard!!!!")

        elif search(r"\blunch\b", message, IGNORECASE):
            self.sendmsg("you should try the adtran creme ;)")

        elif search(r"(\bfight\ssong\b)", message, IGNORECASE):
            fightSong = ''.join(sample(fightSongLyrics, 3))
            self.sendmsg("GO ADTRAN!!! DUN DUN DUNNNN!!!")
            self.sendmsg(fightSong)
            self.sendmsg("ADTRAN! ADTRAN! GOOOOOOOOO ADTRAN!!!!")
            self.sendmsg("*applause*")


def main():
    f = protocol.ReconnectingClientFactory()
    f.protocol = ChiefExecBot

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()

while 1:
    main()
