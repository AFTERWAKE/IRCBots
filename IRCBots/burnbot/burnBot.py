from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, defer
from re import search, IGNORECASE
import random
import time
import os

serv_ip = "coop.test.adtran.com"
serv_port = 6667


class burnBot(irc.IRCClient):

    nickname = "burnBot"
    channel = "#main"
    owner = 'mreams800w7p.adtran.com'
    owner_name = ""
    currentTime = 0
    default = 'burn berNs'
    botList = [
        "dad", "mom",
        "nodebot", "Magic_Conch",
        "Seahorse", "dootbot",
        "pointbot", "botProtector",
        "QuipBot", "MemeBot", "burnBot", "Mr_HighFive", "theCount", "Doge", "Calculator"]
    user_list = []
    ignoreList = []
    with open(os.path.join(os.getcwd(), 'Responses.txt'), 'r') as file:
            harumph = file.readlines()

    jokes = harumph[0].split("',")
    for i, joke in enumerate(jokes):
        jokes[i] = joke.lstrip(" '")

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
       

        if message.startswith(self.nickname):
            if search(r'(^|\s)+ignore*(\s|$)+', message, IGNORECASE) and user_ip == self.owner:
                self.ignoreList.append(message.split(" ")[2])
            elif search(r'(^|\s)+unignore*(\s|$)+', message, IGNORECASE) and user_ip == self.owner:
                self.ignoreList.remove(message.split(" ")[2])
            elif timeRightNow - self.currentTime > 5:
                self.user_list = [names for names in self.user_list if names not in self.botList]
                if channel == self.nickname and user_ip != self.owner:
                    return
                elif search(r"(^|\s)+say*(!|\?)*(\s|$)", message, IGNORECASE):
                    if user_ip == self.owner:
                        self.msg(self.channel, message.split('say ')[1])
                elif nick in self.ignoreList:
                    return
                elif search(r'(^|\s)+help*(\s|$)+', message, IGNORECASE):
                    self.currentTime = time.time()
                    self.msg(self.channel, "Just point me in the direction of who to burn :^). <warning>Be wary of whom/what you try to burn.</warning>")
                elif search(r"(^|\s)+burn*(!|\?)*(\s|$)", message, IGNORECASE):
                    self.currentTime = time.time()
                    items = message.split(" ")
                    burn_name = ""
                    if len(items) > 2:
                        burn_name = irc.stripFormatting(message.split(" ")[2])
                    if len(items) == 2:
                        self.msg(self.channel, random.choice(self.user_list) + ": " + random.choice(self.jokes))
                    elif burn_name.lower() == self.nickname.lower():
                        self.msg(self.channel, "Burn baby, burn.")
                    elif burn_name.lower() == self.owner_name.lower():
                        self.msg(self.channel, 'Feel the burn')
                    elif burn_name not in self.user_list:
                        if user_ip == self.owner:
                            self.msg(self.channel, burn_name + ": " + random.choice(self.jokes))
                            print (burn_name)
                        else:
                            self.msg(self.channel, "Error 69: User NOT FOUND. Prepare for ultimate burning. \n" + nick
                                + ": " + random.choice(self.jokes))
                    elif burn_name in self.botList:
                        if user_ip == self.owner:
                            self.msg(self.channel, burn_name + ": " + random.choice(self.jokes))
                        else:
                            self.msg(self.channel, "Silly human. Burns are for people. You looking to get burned "
                                 + nick + "?\n" + nick + ": " + random.choice(self.jokes))
                    else:
                        self.msg(self.channel, burn_name + ": " + random.choice(self.jokes))
                print (self.currentTime)

def main():
    f = protocol.ReconnectingClientFactory()
    f.protocol = burnBot

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()

while 1:
    main()
