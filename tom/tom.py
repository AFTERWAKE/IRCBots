from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, defer
from re import search, IGNORECASE
from random import (
                    choice,
                    randint
                    )
import random
import time
import os

serv_ip = "coop.test.adtran.com"
serv_port = 6667

fightSongLyrics = ["I'm in the lake!!! DUN DUN DUNNNN!!!!",
                   "Taylor watch out for those packets! DUN DUN DUN!!!!",
                   "We got TA5Ks!! DUN DUN DUNNNN!!!!",
                   "Cable ART is on fire!! DUN DUN DUNNNN!!!",
                   "Calix is going down!!!! DUN DUN DUNNNN!!!",
                   "We got Gloria rockin at the front desk!! DUN DUN DUN!!!!!",
                   "Let's all go swim in the lake!! DUN DUN DUNNNN!!!",
                   "Dynetics WHO??!! DUN DUN DUNNNN!!!"]

class complimentBot(irc.IRCClient):

    nickname = "tom"
    channel = "#main"
    owner = 'cn-vm-gbeagle.adtran.com'
    owner_name = ""
    currentTime = 0
    default = 'burn berNs'
    botList = ["dad", "Seahorse", "pointbot", "botProtector",
        "QuipBot", "MemeBot", "theCount", "Doge", "Calculator", "complimentBot"]
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
        # for (key, value) in usr:
        #     usr[key] = [(value)]
        if (usr["ip"] == self.owner):
               self.owner_name = usr["nick"]
        self.user_list.append(usr)
        # print self.user_list    
    def irc_RPL_ENDOFWHO(self, *nargs):
            "Called when WHO output is complete"
            print ("Users:")
            for each in self.user_list:
                print (each["nick"] + each["ip"])
				#print (each["ip"])
	# def join(self, channel)
 #    	self.join(channel)	

    def privmsg(self, user, channel, message):
		
        timeRightNow = time.time()
        nick = user.split('!')[0]
        user_ip = user.split('@')[1]
        user_name = []
        for name in self.user_list: user_name.append(name["nick"])

        if search(self.nickname+ r",*\shelp", message, IGNORECASE):
            self.currentTime = timeRightNow
            self.msg(self.channel, "ADTRAN, Inc. is a provider of telecommunications networking equipment and "
                                   "internetworking products. Its headquarters are in Huntsville, Alabama.")
        elif search(r"(\bidea\b)", message, IGNORECASE):
            self.currentTime = timeRightNow
            self.msg(self.channel, "That's a great idea!!")
        elif search(r"(\bhackathon\b)", message, IGNORECASE):
            self.currentTime = timeRightNow
            self.msg(self.channel, "Woooo! Hackathon!!!!")
        elif search(r"(\badtran\b)", message, IGNORECASE):
            self.currentTime = timeRightNow
            self.msg(self.channel, "Goooooo ADTRAN!") 
        elif search(r"(\btom\b)", message, IGNORECASE):
            self.currentTime = timeRightNow
            self.msg(self.channel, "It's me! Tom!!! On the eighth floor!!!!") 
        elif search(r"(\bta5k\b)", message, IGNORECASE):
            self.currentTime = timeRightNow
            self.msg(self.channel, "You should go with the flamethrower attachment") 
        elif search(r"(\bta5ks\b)", message, IGNORECASE):
            self.currentTime = timeRightNow
            self.msg(self.channel, "our pride and joy the TA5K")
        elif search(r"(\b(rolt|r-olt)\b)", message, IGNORECASE):
            self.currentTime = timeRightNow
            self.msg(self.channel, "Tomothy Remote-Optical-Line-Terminal Stanton is the name, don't wear it out ;)")
        elif search(r"(\bdynetics\b)", message, IGNORECASE):
            self.currentTime = timeRightNow
            self.msg(self.channel, "no cursing in adtran go wash your mouth")
        elif search(r"(\bwork\b)", message, IGNORECASE):
            self.currentTime = timeRightNow
            self.msg(self.channel, "werk werk werk werk")
        elif search(r"(\bcalix\b)", message, IGNORECASE):
            self.currentTime = timeRightNow
            self.msg(self.channel, "no sir")
        elif search(r"(\bworking\b)", message, IGNORECASE):
            self.currentTime = timeRightNow
            self.msg(self.channel, "keep working hard!!!!")
        elif search(r"(\bfight\ssong\b)", message, IGNORECASE):
            self.msg(self.channel, "GO ADTRAN!!! DUN DUN DUNNNN!!!")
            self.currentTime = timeRightNow
            self.msg(self.channel, random.choice(fightSongLyrics))
            self.currentTime = timeRightNow
            self.msg(self.channel, random.choice(fightSongLyrics))
            self.currentTime = timeRightNow
            self.msg(self.channel, random.choice(fightSongLyrics))
            self.currentTime = timeRightNow
            self.msg(self.channel, "ADTRAN! ADTRAN! GOOOOOOOOO ADTRAN!!!!")
            self.currentTime = timeRightNow
            self.msg(self.channel, "*applause*")



def main():
    f = protocol.ReconnectingClientFactory()
    f.protocol = complimentBot

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()

while 1:
    main()
