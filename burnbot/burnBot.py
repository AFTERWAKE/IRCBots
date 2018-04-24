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
    owner = '172.22.64.214'
    owner_name = "berns"
    currentTime = 0
    default = 'burn berNs'
    botList = [
        "dad", "mom",
        "nodebot", "Magic_Conch",
        "Seahorse", "dootbot",
        "pointbot", "botProtector",
        "QuipBot", "MemeBot", "burnBot", "Mr_HighFive"]
    user_list = []

    with open(os.path.join(os.getcwd(), 'Responses.txt'), 'r') as file:
            harumph = file.readlines()

    jokes = harumph[0].split("',")
    for i, joke in enumerate(jokes):
        jokes[i] = joke.lstrip(" '")


    def signedOn(self):
        self.join(self.channel)
        self.who(self.channel)

    def irc_unknown(self, prefix, command, params):
        print "ERROR", prefix, command, params

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
        usr["nick"] = nargs[1][5]
        usr["host"] = nargs[1][2]
        usr["ip"] = nargs[1][3]
        self.user_list.append(usr["nick"])

    def irc_RPL_ENDOFWHO(self, *nargs):
            "Called when WHO output is complete"
            print "Users:"
            for each in self.user_list:
                print each
            print self.user_list
    def privmsg(self, user, channel, message):

        if message.startswith(self.nickname):
            nick = user.split('!')[0]
            user_ip = user.split('@')[1]

            if channel == self.nickname and user_ip != self.owner:
                return
            if search(r'(^|\s)+help*(\s|$)+', message, IGNORECASE):
                currentTime = time.time()
                self.msg(self.channel, "Just point me in the direction of who to burn :^)")
            elif search(r"(^|\s)+say*(!|\?)*(\s|$)", message, IGNORECASE):
                if user_ip == self.owner:
                    self.msg(self.channel, message.split('say ')[1])
            elif search(r"(^|\s)+burn*(!|\?)*(\s|$)", message, IGNORECASE):
                burn_name = message.split(" ")[2]
                if burn_name.lower() == self.nickname.lower():
                    self.msg(self.channel, "Burn baby, burn.")
                elif burn_name.lower() == self.owner_name.lower():
                    self.msg(self.channel, 'Feel the burn')
                elif burn_name not in self.user_list:
                    if user_ip == self.owner:
                        self.msg(self.channel, burn_name + ": " + random.choice(self.jokes))
                        print burn_name
                    else:
                        self.msg(self.channel, "Error 69: User NOT FOUND. Prepare for ultimate burning. \n" + nick + ": " + random.choice(self.jokes))
                elif (burn_name) in self.botList:
                    self.msg(self.channel, "Silly human. Burns are for people. You looking to get burned " + nick + "?\n"
                             + nick + ": " + random.choice(self.jokes))

                else:
                    self.msg(self.channel, burn_name + ": " + random.choice(self.jokes))
                    

            elif search(r"(^|\s)+attack*(!|\?)*(\s|$)", message, IGNORECASE):
                self.msg(self.channel, 'what a loser tb is')

def main():
    f = protocol.ReconnectingClientFactory()
    f.protocol = burnBot

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()

while 1:
    main()
