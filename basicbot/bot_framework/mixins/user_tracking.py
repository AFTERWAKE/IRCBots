class UserTracking(object):
  def __init__(self):
    super(UserTracking, self).__init__()
    self._users = {}
    
  """ Public utilities """
  def get_user_from_nick(self, nick):
    for user in self._users:
      if self.get_nick_from_user(user) == nick:
        return user
    return None
    
  """ Overload in derivatives/mixins to initialize any extra user data (use super) """
  def add_user(self, user):
    self._users[user] = {}
    
  """ Twisted function overrides """
  def joined(self, channel):
    self._send_who_request(channel)
    
  def userJoined(self, nick, channel):
    self._send_who_request(nick)
    
  def userLeft(self, nick, channel):
    self._remove_user_by_nick(nick)
    
  def userQuit(self, nick, quitMessage):
    self._remove_user_by_nick(nick)
  
  def userRenamed(self, oldNick, newNick):
    self._remove_user_by_nick(oldNick)
    self._send_who_request(newNick)
    
  def irc_RPL_WHOREPLY(self, prefix, params):
    # params: me, chan, uname, host, server, nick, modes, realname
    # want in form nick!uname@host
    user = "{}!{}@{}".format(params[5], params[2], params[3])
    if user not in self._users and params[5] != self.nickname:
      self.add_user(user)
    
  """ Private Methods """
  def _send_who_request(self, target):
    self.sendLine("WHO {}".format(target))
    
  def _remove_user_by_nick(self, nick):
    if self.get_user_from_nick(nick):
      del self._users[self.get_user_from_nick(nick)]
    else:
      print("ERROR: Could not find user of nick {}".format(nick))