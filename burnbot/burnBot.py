from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from re import search, IGNORECASE
import random
import time

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
    userList = []

    # page = requests.get('https://humoropedia.com/best-comebacks-n-funny-insults/')
    # page2= requests.get('http://www.lovepanky.com/my-life/work-and-office/awesomely-insulting-good-comebacks')
    # tree = html.fromstring(page.content)
    # tree2 = html.fromstring(page2.content)
    # jokes = tree.xpath('//li/text()')
    # jokes2 = tree2.xpath('//p/text()')
    # jokes = jokes + jokes2

    thefile = open('C:\Users\\bmoussad\PycharmProjects\maBoi\Responses.txt', 'r')
    with open ('Responses.txt', 'r') as file:
            harumph = file.readlines()

    jokes = harumph[0].split("',")
    for i, joke in enumerate(jokes):
        jokes[i] = joke.lstrip(" '")


    def signedOn(self):
        self.join(self.channel)

    def irc_unknown(self, prefix, command, params):
        print "ERROR", prefix, command, params

    def privmsg(self, user, channel, message):

        # userList = RPL_NAMREPLY


        if message.startswith(self.nickname):
            nick = user.split('!')[0]
            user_ip = user.split('@')[1]


            # if burn_name not in (userList or self.botList):
            #     return
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
                elif burn_name not in self.userList:
                    if user_ip == self.owner:
                        self.msg(self.channel, burn_name + ": " + random.choice(self.jokes))
                        print burn_name
                    else:
                        return
                elif (burn_name) in self.botList:
                    self.msg(self.channel, "Silly human. Burns are for people. You looking to get burned " + nick + "?\n"
                             + nick + ": " + random.choice(self.jokes))
                elif burn_name.lower() == self.owner_name.lower():
                    self.msg(self.channel, 'Feel the burn')
                else:
                    self.msg(self.channel, burn_name + ": " + random.choice(self.jokes))
                    

            elif search(r"(^|\s)+attack*(!|\?)*(\s|$)", message, IGNORECASE):
                self.msg(self.channel, 'what a loser tb is')
    def update_user (self, channel):
        self.sendLine('WHO %s' % channel)


def main():
    f = protocol.ReconnectingClientFactory()
    f.protocol = burnBot

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()

while 1:
    main()