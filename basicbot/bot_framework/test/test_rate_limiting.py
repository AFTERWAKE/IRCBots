import unittest
from bot_core import BotCore
from mixins.rate_limiting import RateLimiting
from test_user_tracking import UserTrackingBotSpy
  
class RateLimitingTest(unittest.TestCase):
  def setUp(self):  
    self.bot = RateLimitingBotSpy()
    self.bot.set_channel_rate_limit(5)
    self.bot.set_pm_rate_limit(3)
    
  def test_invalid_rate_limits_raise_exception(self):
    with self.assertRaises(ValueError):
      self.bot.set_channel_rate_limit("eight")
    with self.assertRaises(ValueError):
      self.bot.set_pm_rate_limit("four")
    
  def test_bot_join_adds_extra_user_data_correctly(self):
    self.assertEquals(self.bot._users, {"a!uname@user.com":{"lastpm":0}, 
      "b!uname@user.com":{"lastpm":0}, "c!uname@user.com":{"lastpm":0}})
      
  def test_admin_ignores_channel_rate_limit(self):
    self.bot.rate_limit()
    self.bot.privmsg("x!uname@admin.com", "#main", "testbot, user")
    self.assertEquals(self.bot.output, "USER")
    
  def test_admin_ignores_pm_rate_limit(self):
    self.bot.rate_limit()
    self.bot.privmsg("x!uname@admin.com", "testbot", "pm")
    self.assertEquals(self.bot.output, "PM")
    
  def test_channel_rate_limit_blocks_user_messages(self):
    self.bot.rate_limit()
    self.bot.privmsg("a!uname@user.com", "#main", "testbot, user")
    self.assertEquals(self.bot.output, "")
    
  def test_channel_not_rate_limited_user_can_send(self):
    self.bot.un_rate_limit()
    self.bot.privmsg("a!uname@user.com", "#main", "testbot, user")
    self.assertEquals(self.bot.output, "USER")
    
  def test_pm_rate_limit_blocks_user_messages(self):
    self.bot.rate_limit()
    self.bot.privmsg("a!uname@user.com", "testbot", "pm")
    self.assertEquals(self.bot.output, "")
    
  def test_pm_not_rate_limited_user_can_send(self):
    self.bot.un_rate_limit()
    self.bot.privmsg("a!uname@user.com", "testbot", "pm")
    self.assertEquals(self.bot.output, "PM")
    

class RateLimitingBotSpy(RateLimiting, UserTrackingBotSpy):
  def __init__(self):
    super(RateLimitingBotSpy, self).__init__()
    self.is_rate_limited = False
    
  def rate_limit(self):
    self.is_rate_limited = True
    
  def un_rate_limit(self):
    self.is_rate_limited = False
  
  """ Overrides from RateLimiting so not time-dependent """
  def _is_channel_rate_limited(self):
    return self.is_rate_limited
      
  def _is_pm_rate_limited(self, user):
    return self.is_rate_limited
    
if __name__ == "__main__":
  unittest.main()