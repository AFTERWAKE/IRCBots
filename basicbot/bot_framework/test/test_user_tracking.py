import unittest
from bot_core import BotCore
from utils import TestBotSpy
from mixins.user_tracking import UserTracking
  
class UserTrackingTest(unittest.TestCase):
  def setUp(self):  
    self.bot = UserTrackingBotSpy()
    
  def test_bot_join_adds_channel_users_correctly(self):
    self.assertEquals(self.bot._users, {"a!uname@user.com":{}, 
      "b!uname@user.com":{}, "c!uname@user.com":{}})
      
  def test_user_join_adds_user_correctly(self):
    self.bot.userJoined("f", "#main")
    self.assertEquals(self.bot._users, {"a!uname@user.com":{}, 
      "b!uname@user.com":{}, "c!uname@user.com":{}, "f!uname@user.com":{}})
      
  def test_user_left_removes_user_correctly(self):
    self.bot.userLeft("b", "#main")
    self.assertEquals(self.bot._users, {"a!uname@user.com":{}, "c!uname@user.com":{}})
    
  def test_user_quit_removes_user_correctly(self):
    self.bot.userQuit("a", "#main")
    self.assertEquals(self.bot._users, {"b!uname@user.com":{}, "c!uname@user.com":{}})
    
  def test_user_renamed_updates_user_correctly(self):
    self.bot.userRenamed("b", "k")
    self.assertEquals(self.bot._users, {"a!uname@user.com":{}, 
      "k!uname@user.com":{}, "c!uname@user.com":{}})
      
  def test_get_user_from_nick(self):
    user = self.bot.get_user_from_nick("a")
    self.assertEquals(user, "a!uname@user.com")
    

class UserTrackingBotSpy(UserTracking, TestBotSpy):
  """ Override from UserTracking so don't need server call """
  def __init__(self):
    super(UserTrackingBotSpy, self).__init__()
    self.joined(self.channel)
    
  def _send_who_request(self, target):
    if target == self.channel:
      target = ["a", "b", "c"]
    for nick in target:
      self.irc_RPL_WHOREPLY(None, [None, None, "uname", "user.com", 
        None, nick, None, None])
    
    
if __name__ == "__main__":
  unittest.main()