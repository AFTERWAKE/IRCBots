import time
import argparse
import exceptions
import re
import random
from bot_framework import BotCore, BotFactory, mixins
from twisted.internet import reactor

class BasicBot(mixins.BasicCommands, mixins.Ignoring,
               mixins.RateLimiting, mixins.PrintOnlyPMs,
               BotCore):
    def __init__(self):
        super(BasicBot, self).__init__()
        self.set_channel_rate_limit(7)
        self.set_pm_rate_limit(3)
        self.__last_response = 0 # this should go into bot core

    def help_message(self):
        self.msg(self.channel, "Hello, it's me, {0}. I'm BotCore with some features! "
                "If you're an admin, run the \"show\" command to see what I can do. If you're "
                "a user, have a day (or say {0}, commands).".format(self.nickname))

    def ls(self):
        # responses = [""]
        # self.msg(channel, random.choice(responses))
        self.msg(self.channel, "pi@raspberrypi:~ $ ls\n")
        self.msg(self.channel, "go  IRCBots  run_bots.sh  u  IDIOT\n")

    def privmsg(self, user, channel, message):
        user_name = user.split("!")[0]
        user_ip = user.split("@")[1]
        try:
            host = re.match(r"\w+!~(\w+)@", user).group(1)
        except exceptions.AttributeError:
            host = ""
        temp_time = time.time()

        # pm privilages
        if (channel == self.nickname) and user_ip != admin_ip:
            return

        # print(channel, user, message)
        if (temp_time - self.__last_response > 5) or user.split("@")[1] == admin_ip:
            # admin commands
            # if user_ip == admin_ip:
            #     self.admin_cmds(channel, message)

            # # ignore list
            # if host in self.__ignore:
            #     return

            if False:
                pass

            elif re.search(self.nickname + r",*\shelp", message):
                self.help_message()

            elif re.search(r"\bls", message.lower()):
                self.ls()

            else:
                return


def main():
    f = BotFactory(BasicBot())
    f.set_bot_config(args.nick, args.channel, args.admin)
    reactor.connectTCP(args.server, 6667, f)
    reactor.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
            "This bot connects to an IRC channel and does stuff.")
    parser.add_argument("server", help="the server to join")
    parser.add_argument("-a", "--admin", help="the host of the admin; needed to "
            "run admin commands", metavar='ADM', default="0.0.0.0")
    parser.add_argument("-c", "--channel", help="the channel on the server to "
            "join (default: %(default)s)", default="#main", metavar='CH')
    parser.add_argument("-n", "--nick", help="the nick of the bot "
            "(default: %(default)s)", default="basicbot")
    args = parser.parse_args()

    main()

