import pickle
from time import time
from datetime import datetime
from re import match, IGNORECASE


class PrintAllMessages(object):
  def privmsg(self, user, channel, message):
      time = datetime.now()
      print ("[{:02d}:{:02d}:{:02d}] {} @ {}: {}".format(time.hour,
        time.minute, time.second, user, channel, message))
      super(PrintAllMessages, self).privmsg(user, channel, message)
      

class UserTracking(object):
  def __init__(self):
    super(UserTracking, self).__init__()
    self._users = {}
    
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
      self._add_user(user)
      
  def _add_user(self, user):
    self._users[user] = {}
          
  def _send_who_request(self, target):
    self.sendLine("WHO {}".format(target))
    
  def _remove_user_by_nick(self, nick):
    if self.get_user_from_nick(nick):
      del self._users[self.get_user_from_nick(nick)]
    else:
      print("ERROR: Could not find user of nick {}".format(nick))
          
  def get_user_from_nick(self, nick):
    for user in self._users:
      if self.get_nick_from_user(user) == nick:
        return user
    return None
    
    
class EnableRateLimiting(UserTracking):
  def __init__(self):
    super(EnableRateLimiting, self).__init__()
    self._channel_rate_limit = 0
    self._pm_rate_limit = 0
    self._last_channel_message = 0
    
  def _add_user(self, user):
    super(EnableRateLimiting, self)._add_user(user)
    self._users[user].update({"lastpm": 0})
    
  def set_channel_rate_limit(self, seconds):
    self._channel_rate_limit = seconds
    
  def set_pm_rate_limit(self, seconds):
    self._pm_rate_limit = seconds
    
  def privmsg(self, user, channel, message):
    if self.is_admin(user):
      super(EnableRateLimiting, self).privmsg(user, channel, message)
    elif channel == self.channel and not self._is_channel_rate_limited():
      super(EnableRateLimiting, self).privmsg(user, channel, message)
      self._last_channel_message = time()
    elif channel == self.nickname and not self._is_pm_rate_limited(user):
      super(EnableRateLimiting, self).privmsg(user, channel, message)
      self._users[user]["lastpm"] = time()
      
  def _is_channel_rate_limited(self):
    return (time() - self._last_channel_message < self._channel_rate_limit)
      
  def _is_pm_rate_limited(self, user):
    return (time() - self._users[user]["lastpm"] < self._pm_rate_limit)
    

class EnableIgnore(object):
  def __init__(self):
    super(EnableIgnore, self).__init__()
    self._ignoreMasks = []
    
    self.register_savedata(self._ignoreMasks)
    self.register_command("ignore", "ADMIN", self.cmd_ignore)
    self.register_command("unignore", "ADMIN", self.cmd_unignore)
    
  def print_debug(self):
    super(EnableIgnore, self).print_debug()
    print("Ignore Masks: {}".format(self._ignoreMasks))
    
  def cmd_ignore(self, mask):
    "Usage: ignore <mask>, adds mask in the format nick!uname@host to ignore list."
    try:
      self.add_ignore_mask(mask)
      print("Successfully added ignore mask '{}'".format(mask))
    except InvalidMask:
      print("Invalid mask '{}'".format(mask))
    except DuplicateMask:
      print("Duplicate mask '{}'".format(mask))
            
  def cmd_unignore(self, mask):
    "Usage: unignore <mask>, removes mask from ignore list."
    try:
      self.remove_ignore_mask(mask)
      print("Successfully removed ignore mask '{}'".format(mask))
    except InvalidMask:
      print("Could not find mask '{}'".format(mask))
    
  def privmsg(self, user, channel, message):
    if not self._is_ignored(user) or self.is_admin(user):
      super(EnableIgnore, self).privmsg(user, channel, message)
    
  def add_ignore_mask(self, mask):
    if not self._valid_mask(mask):
      raise InvalidMask
    if mask in self._ignoreMasks:
      raise DuplicateMask
    self._ignoreMasks.append(mask)
    
  def remove_ignore_mask(self, mask):
    if mask not in self._ignoreMasks:
      raise InvalidMask
    self._ignoreMasks.remove(mask)
    
  def _is_ignored(self, user):
    for mask in self._ignoreMasks:
      mask_regex = mask.replace('*', '.*')
      if match(mask_regex, user, flags=IGNORECASE):
        return True
    return False
    
  # Matches user string in the format nick!uname@host
  @staticmethod
  def _valid_mask(mask):
    return match("^(.+|\*)!(.+|\*)@(.+|\*)$", mask) is not None
    
    
class InvalidMask(Exception):
  pass
  
class DuplicateMask(Exception):
  pass