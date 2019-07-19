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
    owner = 'bmoussadcomp.adtran.com'
    owner_name = ''
    currentTime = 0
    with open(os.path.join(os.getcwd(), 'bot_list.txt'), 'r') as f:
        botList = [bot.strip('\n') for bot in f.readlines()]
    user_list = []
    ignoreList = []
    with open(os.path.join(os.getcwd(), 'responses.txt'), 'r') as f:
            responses = f.readlines()

    jokes = responses[0].split("',")
    for i, joke in enumerate(jokes):
        jokes[i] = joke.lstrip(" '")

    def signedOn(self):
        self.join(self.channel)
        self.who(self.channel)

    def irc_unknown(self, prefix, command, params):
        print("ERROR", prefix, command, params)

    def userJoined(self, user, channel):
        print(user, "has joined")
        self.who(self.channel)

    def userQuit(self, user, channel):
        print(user, "has quit")
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
        usr["nick"] = nargs[1][5]
        usr["host"] = nargs[1][2]
        usr["ip"] = nargs[1][3]
        try:
            if (usr["ip"] == self.owner and usr["nick"] not in self.botList):
                self.owner_name = usr["nick"]
                print('Owner:', self.owner_name)
        except:
            print("No owner found")
        self.user_list.append(usr)
 
    def irc_RPL_ENDOFWHO(self, *nargs):
            "Called when WHO output is complete"
            print("Users:")
            for each in self.user_list:
                print(each["nick"], each["ip"])

    def privmsg(self, user, channel, message):
        timeRightNow = time.time()
        nick = user.split('!')[0]
        user_ip = user.split('@')[1]
        user_name = []
        for name in self.user_list: user_name.append(name["nick"])
        self.user_list = [names for names in self.user_list if names not in self.botList]
        if message.startswith(self.nickname):
            if search(r'(^|\s)+ignore*(\s|$)+', message, IGNORECASE) and user_ip == self.owner:
                self.ignoreList.append(message.split(" ")[2])
            elif search(r'(^|\s)+unignore*(\s|$)+', message, IGNORECASE) and user_ip == self.owner:
                self.ignoreList.remove(message.split(" ")[2])
            elif timeRightNow - self.currentTime > 5:
                if channel == self.nickname and user_ip != self.owner:
                    return
                elif search(r"(^|\s)+say*(!|\?)*(\s|$)", message, IGNORECASE):
                    if user_ip == self.owner:
                        self.msg(self.channel, message.split('say ')[1])
                elif nick in self.ignoreList:
                    return
                elif search(r'(^|\s)+help*(\s|$)+', message, IGNORECASE):
                    self.help()
                elif search(r"(^|\s)+burn*(!|\?)*(\s|$)", message, IGNORECASE):
                    self.burn(message, user_name, user_ip, nick)

    def burn(self, message, user_name, user_ip, nick):
        self.currentTime = time.time()
        items = message.split(" ")
        burn_name = ""
        if len(items) > 2:
            burn_name = irc.stripFormatting(message.split(" ")[2])
        if len(items) == 2:
            self.msg(self.channel, random.choice(user_name) + ": " + random.choice(self.jokes))
        elif burn_name.lower() == self.nickname.lower():
            self.msg(self.channel, "Burn baby, burn.")
        elif burn_name.lower() == self.owner_name.lower():
            self.msg(self.channel, 'Feel the burn')
        elif burn_name not in user_name:
            if user_ip == self.owner:
                self.msg(self.channel, burn_name + ": " + random.choice(self.jokes))
            else:
                self.user_not_found(nick)
        elif burn_name in self.botList:
            self.anti_bot_burn(user_ip, burn_name, nick)
        else:
            self.msg(self.channel, burn_name + ": " + random.choice(self.jokes))

    def user_not_found(self, nick):
        self.msg(self.channel, "Error 69: User NOT FOUND. Prepare for ultimate burning. \n" + nick
            + ": " + random.choice(self.jokes))

    def help(self):
        self.currentTime = time.time()
        self.msg(self.channel, "Just point me in the direction of who to burn. Just don't get burned yourself. ;^)")

    def anti_bot_burn(self, user_ip, burn_name, nick):
        anti_message = f"Silly human. Burns are for people.\n{nick}: {random.choice(self.jokes)}"
        if user_ip == self.owner:
            self.msg(self.channel, f"{burn_name}: {random.choice(self.jokes)}")
        else:
            self.msg(self.channel, anti_message)

def main():
    f = protocol.ReconnectingClientFactory()
    f.protocol = burnBot

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()

if __name__ == "__main__":
    main()
