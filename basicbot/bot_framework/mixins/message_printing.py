from datetime import datetime

class PrintAllMessages(object):
  def privmsg(self, user, channel, message):
    time = datetime.now()
    print ("[{:02d}:{:02d}:{:02d}] {} @ {}: {}".format(time.hour,
      time.minute, time.second, user, channel, message))
    super(PrintAllMessages, self).privmsg(user, channel, message)
    
class PrintOnlyPMs(object):
  def privmsg(self, user, channel, message):
    if (channel == self.nickname):
      time = datetime.now()
      print ("[{:02d}:{:02d}:{:02d}] (PM) {}: {}".format(time.hour,
        time.minute, time.second, user, message))
    super(PrintOnlyPMs, self).privmsg(user, channel, message)