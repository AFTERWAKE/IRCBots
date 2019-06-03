from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, defer
from re import search, IGNORECASE
import random
import time
import os

serv_ip = "coop.test.adtran.com"
serv_port = 6667


class complimentBot(irc.IRCClient):

    nickname = "niceBot"
    channel = "#main"
    owner = 'tarp-coop-ubuntu.adtran.com'
    owner_name = ""
    currentTime = 0
    default = 'burn berNs'
    botList = [
        "dad", "mom",
        "nodebot", "Magic_Conch",
        "Seahorse", "dootbot",
        "pointbot", "botProtector",
        "QuipBot", "MemeBot", "Mr_HighFive", "theCount", "Doge", "Calculator", "complimentBot"]
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
        user_name = []
        for name in self.user_list: user_name.append(name["nick"])

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
                    self.msg(self.channel, "I love all the adtran co-ops with all my heart, and with so much hatred in this irc (@berns @burnbot), I would like to spread some kindess. Give me someone to compliment!")
                elif search(r'(^|\s)+attack*(\s|$)+', message, IGNORECASE):
                    self.currentTime = time.time()
                    self.msg(self.channel, "I will not \n")
                elif search(r"(^|\s)+compliment*(!|\?)*(\s|$)", message, IGNORECASE):
                    self.currentTime = time.time()
                    items = message.split(" ")
                    burn_name = ""
                    if len(items) > 2:
                        burn_name = irc.stripFormatting(message.split(" ")[2])
                    if len(items) == 2:
                        self.msg(self.channel, random.choice(user_name) + ": " + random.choice(self.jokes))
                    elif burn_name.lower() == self.nickname.lower():
                        self.msg(self.channel, "self love <3." + "\n" + self.nickname.lower() + ": " + random.choice(self.jokes))
                    elif burn_name.lower() == self.owner_name.lower():
                        self.msg(self.channel, "she\'s the best, isn\'t she?" + "\n" + self.owner_name.lower() + ": " + random.choice(self.jokes))
                    elif burn_name.lower() == "burnbot":
                        self.msg(self.channel, "burnBot: I'm rubber and you're glue...")
                    elif burn_name not in user_name:
                        if user_ip == self.owner:
                            self.msg(self.channel, burn_name + ": " + random.choice(self.jokes))
                            print (burn_name)
                        else:
                            self.msg(self.channel, "Fiddle sticks! User not found. Prepare for ultimate compliments. \n" + nick
                                + ": " + random.choice(self.jokes))
                    elif burn_name in self.botList:
                        if user_ip == self.owner:
                            self.msg(self.channel, burn_name + ": " + random.choice(self.jokes))
                        else:
                            self.msg(self.channel, "Sweet human. Compliments are really only meant for people. Here's one for you anyway "
                                 + nick + "<3 \n" + nick + ": " + random.choice(self.jokes))
                    else:
                        self.msg(self.channel, burn_name + ": " + random.choice(self.jokes))
                print (self.currentTime)

def main():
    f = protocol.ReconnectingClientFactory()
    f.protocol = complimentBot

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()

while 1:
    main()