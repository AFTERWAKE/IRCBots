import unittest
from datetime import datetime
from bot_core import BotCore
from utils import TestBotSpy
from mixins.basic_commands import BasicCommands
  
class BasicCommandsTest(unittest.TestCase):
  def setUp(self):  
    self.bot = BasicCommandsBotSpy()
    
  def test_help_command(self):
    self.bot.privmsg("a!uname@user.com", "#main", "testbot, help")
    self.assertEqual(self.bot.output, "MSG to #main: Hello, it's me, testbot.")
    
  def test_say_command_no_words_sends_usage(self):
    self.bot.privmsg("x!uname@admin.com", "#main", "testbot, say")
    self.assertEqual(self.bot.output, "MSG to x: Usage: say <message>, sends message to channel")
    
  def test_say_command_with_message_returns_expected_output(self):
    self.bot.privmsg("x!uname@admin.com", "testbot", "say Hello, everyone!!! I am testbot :))")
    self.assertEqual(self.bot.output, "MSG to #main: Hello, everyone!!! I am testbot :))")
    
  def test_me_command_no_words_sends_usage(self):
    self.bot.privmsg("x!uname@admin.com", "testbot", "me")
    self.assertEqual(self.bot.output, "MSG to x: Usage: me <message>, sends action to channel")
    
  def test_me_command_with_action_returns_expected_output(self):
    self.bot.privmsg("x!uname@admin.com", "testbot", "me passes a test")
    self.assertEqual(self.bot.output, "ME (#main): passes a test")
    
  def test_quit_command_no_words_blank_quit_message(self):
    self.bot.privmsg("x!uname@admin.com", "testbot", "quit")
    self.assertEqual(self.bot.output, "QUIT: ()")
    
  def test_quit_command_with_message_quits_with_message(self):
    self.bot.privmsg("x!uname@admin.com", "testbot", "quit because i'm tired")
    self.assertEqual(self.bot.output, "QUIT: (because i'm tired)")
    
  def test_get_command_list_utility(self):
    self.assertEqual(self.bot._get_commands("ADMIN"), ["me", "quit", "show", "admin", "say"])
    self.assertEqual(self.bot._get_commands("USER"), ["commands", "help", "user"])
    self.assertEqual(self.bot._get_commands("PM"), ["pm"])
    

class BasicCommandsBotSpy(BasicCommands, TestBotSpy):
  """ Override Twisted methods """
  def describe(self, channel, action):
    self.output += "ME ({}): {}".format(channel, action)
    
  def quit(self, reason=""):
    self.output += "QUIT: ({})".format(reason)
    
if __name__ == "__main__":
  unittest.main()