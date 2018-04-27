from time import time
from user_tracking import UserTracking

class RateLimiting(UserTracking):
  def __init__(self):
    super(RateLimiting, self).__init__()
    self._channel_rate_limit = 0
    self._pm_rate_limit = 0
    self._last_channel_message = 0
    
  """ Public interface """
  def set_channel_rate_limit(self, seconds):
    self._channel_rate_limit = float(seconds)
    
  def set_pm_rate_limit(self, seconds):
    self._pm_rate_limit = float(seconds)
    
  """ Overloaded from BotCore """
  def show(self):
    super(RateLimiting, self).show()
    print("Rate limits: Channel {} seconds, PM {} seconds"
      .format(self._channel_rate_limit, self._pm_rate_limit))
    
  """ Overloaded from BasicUserTracking """
  def add_user(self, user):
    super(RateLimiting, self).add_user(user)
    self._users[user].update({"lastpm": 0})
    
  """ Twisted method overrides """
  def privmsg(self, user, channel, message):
    if self.is_admin(user):
      super(RateLimiting, self).privmsg(user, channel, message)
    elif channel == self.channel and not self._is_channel_rate_limited():
      super(RateLimiting, self).privmsg(user, channel, message)
      self._last_channel_message = time()
    elif channel == self.nickname and not self._is_pm_rate_limited(user):
      super(RateLimiting, self).privmsg(user, channel, message)
      self._users[user]["lastpm"] = time()
  
  """ Private methods """
  def _is_channel_rate_limited(self):
    return (time() - self._last_channel_message < self._channel_rate_limit)
      
  def _is_pm_rate_limited(self, user):
    return (time() - self._users[user]["lastpm"] < self._pm_rate_limit)