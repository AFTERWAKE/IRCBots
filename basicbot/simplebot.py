import mixins
import argparse
from basicbot import BasicBot, BotFactory
from twisted.internet import reactor


class SimpleBot(mixins.EnableRateLimiting, mixins.PrintAllMessages, 
               mixins.EnableIgnore, BasicBot):
  def __init__(self):
    super(SimpleBot, self).__init__()
    self.set_channel_rate_limit(5)
    self.set_pm_rate_limit(3)
    
  def help(self, user):
    self.msg(self.channel, "Hello, it's me, {0}. I'm BasicBot with features! "
      "If you're an admin, run the debug command to see what I can do. If you're "
      "a user, have a day (or say {0}, commands).".format(self.nickname))
      
   
def main():
  f = BotFactory(SimpleBot())
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
    "(default: %(default)s)", default="simplebot")
  args = parser.parse_args()
  
  if args.server:
    main()
  else:
    parser.print_help()