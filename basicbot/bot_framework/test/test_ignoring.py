import unittest
from bot_core import BotCore
from mixins.ignoring import Ignoring
from utils import TestBotSpy
  
class IgnoringTest(unittest.TestCase):
  def setUp(self):  
    self.bot = IgnoringBotSpy()
    
  def test_ignore_by_mask_does_not_format(self):
    self.bot.privmsg("x!uname@admin.com", "#main", "testbot, ignore a!*@ru.biz")
    self.assertEqual(self.bot.output, "MSG to x: a!*@ru.biz added to ignore list")
    
  def test_ignore_by_nick_formats_mask_correctly(self):
    self.bot.privmsg("x!uname@admin.com", "#main", "testbot, ignore a")
    self.assertEqual(self.bot.output, "MSG to x: a!*@* added to ignore list")
    
  def test_ignore_duplicate_mask_returns_error_message(self):
    self.bot.privmsg("x!uname@admin.com", "#main", "testbot, ignore a")
    self.bot.clear_output()
    self.bot.privmsg("x!uname@admin.com", "#main", "testbot, ignore a")
    self.assertEqual(self.bot.output, "MSG to x: Duplicate mask a!*@*")
    
  def test_unignore_by_mask_does_not_format(self):
    self.bot.privmsg("x!uname@admin.com", "#main", "testbot, ignore a!*@ru.biz")
    self.bot.clear_output()
    self.bot.privmsg("x!uname@admin.com", "#main", "testbot, unignore a!*@ru.biz")
    self.assertEqual(self.bot.output, "MSG to x: a!*@ru.biz removed from ignore list")
    
  def test_unignore_by_nick_formats_mask_correctly(self):
    self.bot.privmsg("x!uname@admin.com", "#main", "testbot, ignore a!*@*")
    self.bot.clear_output()
    self.bot.privmsg("x!uname@admin.com", "#main", "testbot, unignore a")
    self.assertEqual(self.bot.output, "MSG to x: a!*@* removed from ignore list")
    
  def test_unignore_unknown_mask_returns_error_message(self):
    self.bot.privmsg("x!uname@admin.com", "#main", "testbot, unignore unknown!what@mask")
    self.assertEqual(self.bot.output, "MSG to x: Could not find mask unknown!what@mask")
    
  def test_ignored_admin_can_send_messages(self):
    self.bot.privmsg("x!uname@admin.com", "#main", "testbot, ignore x")
    self.bot.clear_output()
    self.bot.privmsg("x!uname@admin.com", "#main", "testbot, user")
    self.bot.privmsg("x!uname@admin.com", "testbot", "pm")
    self.assertEqual(self.bot.output, "USERPM")
    
  def test_ignored_user_cannot_send_messages(self):
    self.bot.privmsg("x!uname@admin.com", "#main", "testbot, ignore a")
    self.bot.clear_output()
    self.bot.privmsg("a!uname@user.com", "#main", "testbot, user")
    self.bot.privmsg("a!uname@user.com", "testbot", "pm")
    self.assertEqual(self.bot.output, "")
    
  def test_unignored_user_can_send_messages(self):
    self.bot.privmsg("x!uname@admin.com", "#main", "testbot, ignore a")
    self.bot.privmsg("x!uname@admin.com", "#main", "testbot, unignore a")
    self.bot.clear_output()
    self.bot.privmsg("a!uname@user.com", "#main", "testbot, user")
    self.bot.privmsg("a!uname@user.com", "testbot", "pm")
    self.assertEqual(self.bot.output, "USERPM")
     

class IgnoringBotSpy(Ignoring, TestBotSpy):
  pass
    
if __name__ == "__main__":
  unittest.main()