import os
import unittest
from datetime import datetime
from bot_core import *
from utils import TestBotSpy
  
class BotCoreTest(unittest.TestCase):
  def setUp(self):  
    self.bot = CoreBotSpy()
    
  def test_channel_command_regex(self):
    self.assertIsNone(self.bot._is_channel_command(""))
    self.assertIsNone(self.bot._is_channel_command("help"))
    self.assertIsNone(self.bot._is_channel_command("testbot, "))
    self.assertIsNone(self.bot._is_channel_command("testbothelp"))
    self.assertIsNotNone(self.bot._is_channel_command("testbot, help"))
    self.assertIsNotNone(self.bot._is_channel_command("testbot: help"))
    self.assertIsNotNone(self.bot._is_channel_command("testbot help"))
    
  def test_command_null_name_raises_exception(self):
    with self.assertRaises(InvalidCommand):
      self.bot.register_command("", "ADMIN", self.bot.cmd_admin)
    
  def test_command_invalid_type_raises_exception(self):
    with self.assertRaises(InvalidCommand):
      self.bot.register_command("name", "INVALID TYPE", self.bot.cmd_admin)
      
  def test_time_trigger_invalid_time_raises_exception(self):
    with self.assertRaises(InvalidTime):
      self.bot.register_time_trigger(self.bot.cmd_admin, hour=12, minute=61)
    with self.assertRaises(InvalidTime):
      self.bot.register_time_trigger(self.bot.cmd_admin, hour=25, minute=0)
      
  def test_content_trigger_invalid_trigger_raises_exception(self):
    with self.assertRaises(InvalidMessageTrigger):
      self.bot.register_content_trigger("", self.bot.cmd_admin)
      
  def test_invalid_callback_raises_exception(self):
    with self.assertRaises(InvalidCallback):
      self.bot.register_command("test", "ADMIN", "not a callback")
    with self.assertRaises(InvalidCallback):
      self.bot.register_time_trigger("not a callback")
    with self.assertRaises(InvalidCallback):
      self.bot.register_content_trigger("trigger", "not a callback")
      
  def test_user_command_only_triggers_on_channel_command_message(self):
    self.bot.privmsg("a!uname@user.com", "testbot", "user")
    self.bot.privmsg("a!uname@user.com", "testbot", "testbot, user")
    self.bot.privmsg("a!uname@user.com", "#main", "user")
    self.assertEquals(self.bot.output, "")
    self.bot.privmsg("a!uname@user.com", "#main", "testbot, user")
    self.assertEquals(self.bot.output, "USER")
    
  def test_user_command_incorrect_usage_suppresses_output(self):
    self.bot.privmsg("a!uname@user.com", "#main", "testbot, user INVALID")
    self.assertEquals(self.bot.output, "")
    
  def test_pm_command_only_triggers_on_normal_pm(self):
    self.bot.privmsg("a!uname@user.com", "#main", "pm")
    self.bot.privmsg("a!uname@user.com", "#main", "testbot, pm")
    self.bot.privmsg("a!uname@user.com", "testbot", "testbot, pm")
    self.assertEquals(self.bot.output, "")
    self.bot.privmsg("a!uname@user.com", "testbot", "pm")
    self.assertEquals(self.bot.output, "PM")
    
  def test_pm_command_incorrect_usage_messages_usage_to_caller(self):
    self.bot.privmsg("a!uname@user.com", "testbot", "pm INVALID")
    self.assertEquals(self.bot.output, "MSG to a: Test PM command")
    
  def test_admin_command_normal_user_does_nothing(self):
    self.bot.privmsg("a!uname@user.com", "#main", "admin")
    self.bot.privmsg("a!uname@user.com", "#main", "testbot, admin")
    self.bot.privmsg("a!uname@user.com", "testbot", "admin")
    self.bot.privmsg("a!uname@user.com", "testbot", "testbot, admin")
    self.assertEquals(self.bot.output, "")
    
  def test_admin_command_triggers_on_channel_command_or_normal_pm_from_admin(self):
    self.bot.privmsg("x!uname@admin.com", "testbot", "testbot, admin")
    self.bot.privmsg("x!uname@admin.com", "#main", "admin")
    self.assertEquals(self.bot.output, "")
    self.bot.privmsg("x!uname@admin.com", "testbot", "admin")
    self.assertEquals(self.bot.output, "ADMIN")
    self.bot.privmsg("x!uname@admin.com", "#main", "testbot, admin")
    self.assertEquals(self.bot.output, "ADMINADMIN")
    
  def test_admin_command_incorrect_usage_messages_usage_to_caller(self):
    self.bot.register_command("test", "ADMIN", self.bot.cmd_admin)
    self.bot.privmsg("x!uname@admin.com", "#main", "testbot, admin INVALID")
    self.assertEquals(self.bot.output, "MSG to x: Test ADMIN command")
    
  def test_command_multiple_args_returns_expected_output(self):
    self.bot.register_command("args", "ADMIN", self.bot.cmd_with_args)
    self.bot.privmsg("x!uname@admin.com", "#main", "testbot, args 1 two 3")
    self.assertEquals(self.bot.output, "ARGS: 1, two, 3")

  def test_content_trigger_wrong_trigger_no_output(self):
    self.bot.register_content_trigger("content", self.bot.test_content_trigger)
    self.bot.privmsg("a!uname@user.com", "#main", "CONTENT contint")
    self.assertEquals(self.bot.output, "")
    
  def test_content_trigger_right_trigger_returns_expected_output(self):
    self.bot.register_content_trigger("content", self.bot.test_content_trigger)
    self.bot.privmsg("a!uname@user.com", "#main", "this time i spelled content right")
    self.assertEquals(self.bot.output, "content")
    
  def test_content_trigger_ignore_case_triggers_for_lower_and_upper(self):
    self.bot.register_content_trigger("content", self.bot.test_content_trigger, ignoreCase=True)
    self.bot.privmsg("a!uname@user.com", "#main", "CONTENT")
    self.bot.privmsg("a!uname@user.com", "#main", "content")
    self.assertEquals(self.bot.output, "contentcontent")
    
  def test_time_trigger_called_wrong_time_no_output(self):
    self.bot.register_time_trigger(self.bot.test_time_trigger, hour=8, minute=30)
    self.bot._check_time_triggers(fakeHour=10, fakeMinute=30)
    self.assertEquals(self.bot.output, "")
    
  def test_time_trigger_called_right_time_returns_expected_output(self):
    self.bot.register_time_trigger(self.bot.test_time_trigger, hour=8, minute=30)
    self.bot._check_time_triggers(fakeHour=8, fakeMinute=30)
    self.assertEquals(self.bot.output, "time")
    
  def test_save_and_restore(self):
    data_to_track = [1,2,3]
    self.bot.register_savedata(data_to_track)
    data_to_track.append("a")
    self.bot._save_data()
    
    del data_to_track[:]
    self.bot._restore_data()
    self.assertEquals(data_to_track, [1,2,3,"a"])
    os.remove(self.bot._get_save_path())
    

class CoreBotSpy(TestBotSpy):
  def _check_time_triggers(self, fakeHour=None, fakeMinute=None):
    for hour, minute, callback in self._time_triggers:
      if hour is None or fakeHour == hour:
        if minute is None or fakeMinute == minute:
          callback()
    
  def cmd_with_args(self, caller, a, b, c):
    self.output += "ARGS: {}, {}, {}".format(a, b, c)
    
  def test_content_trigger(self, user, channel, message):
    self.output += "content"
    
  def test_time_trigger(self):
    self.output += "time"
        
   
if __name__ == "__main__":
  unittest.main()