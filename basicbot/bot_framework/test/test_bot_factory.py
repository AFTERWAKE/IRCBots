import unittest
from bot_factory import *

# Only need to test config validation, other functions tested by Twisted
class BotFactoryTest(unittest.TestCase):

  def setUp(self):
    self.factory = TestFactory(BotDummy())
      
  def test_nick_regex(self):
    self.assertFalse(self.factory._valid_nick(""))
    self.assertFalse(self.factory._valid_nick("nickistoolong"))
    self.assertFalse(self.factory._valid_nick("3num"))
    self.assertFalse(self.factory._valid_nick("-dash"))
    
    self.assertTrue(self.factory._valid_nick("valid"))
    self.assertTrue(self.factory._valid_nick("v4l1d"))
    self.assertTrue(self.factory._valid_nick("valid-"))
    self.assertTrue(self.factory._valid_nick("_\[]{}`-"))
    
  def test_channel_regex(self):
    self.assertFalse(self.factory._valid_channel(""))
    self.assertFalse(self.factory._valid_channel("wrongbeginningcharacter"))
    self.assertFalse(self.factory._valid_channel("#has,comma"))
    self.assertFalse(self.factory._valid_channel("#has:colon"))
    
    self.assertTrue(self.factory._valid_channel("#valid"))
    self.assertTrue(self.factory._valid_channel("&valid"))
    self.assertTrue(self.factory._valid_channel("#$^&*([wack.but.valid]3298d-++"))
    
  def test_admin_regex(self):
    self.assertFalse(self.factory._valid_admin(""))
    self.assertFalse(self.factory._valid_admin("1.2.3"))
    self.assertFalse(self.factory._valid_admin("1.2.3.4.5"))
    self.assertFalse(self.factory._valid_admin("256.256.256.256"))
    self.assertFalse(self.factory._valid_admin("www.%@!#&^*.com"))
    self.assertFalse(self.factory._valid_admin("bad_domain.123"))
    
    self.assertTrue(self.factory._valid_admin("0.0.0.0"))
    self.assertTrue(self.factory._valid_admin("1.2.3.4"))
    self.assertTrue(self.factory._valid_admin("255.255.255.255"))
    self.assertTrue(self.factory._valid_admin("24hr.irc.com"))
    self.assertTrue(self.factory._valid_admin("shady.website.ru.info.biz"))
    
  def test_create_bot_null_config_raises_exception(self):
    with self.assertRaises(InvalidConfig):
      self.factory.set_bot_config(None, None, None)
      self.factory._validate_bot_config()
   
class BotDummy(object):
  pass
  
class TestFactory(BotFactory):
  def _validate_bot_config(self):
    if not self.bot.nickname or self._valid_nick(self.bot.nickname):
      raise InvalidConfig
    if not self.bot.channel or self._valid_channel(self.bot.channel):
      raise InvalidConfig
    if not self.bot.channel or self._valid_admin(self.bot.admin):
      raise InvalidConfig   
   
if __name__ == "__main__":
  unittest.main()