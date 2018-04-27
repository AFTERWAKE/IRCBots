from re import match, IGNORECASE
from twisted.internet import protocol

class BotFactory(protocol.ClientFactory, object):
  def __init__(self, bot):
    self.bot = bot
    
  """ Interface for main program """
  def set_bot_config(self, nick, channel, admin):
    self.bot.nickname = nick
    self.bot.channel = channel
    self.bot.admin = admin
    
  """ Twisted method overrides """
  def buildProtocol(self, addr):
    try:
      self._validate_bot_config()
    except InvalidConfig:
      return None
    else:
      self.bot.factory = self
      return self.bot
      
  """ Private methods """
  def _validate_bot_config(self):
    if not self.bot.nickname or not self._valid_nick(self.bot.nickname):
      print("Invalid nick provided. Must be from 1 to 9 characters. "
        "The first character cannot be a digit or a dash.")
      raise InvalidConfig
    if not self.bot.channel or not self._valid_channel(self.bot.channel):
      print("Invalid channel provided. Must be in the form [#|&]<name>. "
              "Cannot have spaces, commas, or semicolons.")
      raise InvalidConfig
    if not self.bot.channel or not self._valid_admin(self.bot.admin):
      print("Invalid host provided. Must be a valid IPv4 address or domain name.")
      raise InvalidConfig
      
  # Matches 1-9 characters. First character can be a letter or special character,
  #   the others can be a letter, special character, or number.
  @staticmethod
  def _valid_nick(nick):
    return match(r"^[a-zA-Z_[\]{}|\\`^][\w[\]{}|\\`^-]{0,8}$", nick,
      flags=IGNORECASE) is not None
    
  # Matches any string beginning with # or & without a space, comma, or colon
  @staticmethod
  def _valid_channel(channel):
    return match(r"^[#|&][^\s,:]*$", channel) is not None
      
  # Matches x.x.x.x, where x is between 0 to 255, or *.com
  @staticmethod  
  def _valid_admin(host):
    octet = "(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])"
    return match(r"^((\w+\.)+[A-Za-z]+|({0}\.){{3}}{0})$"
      .format(octet), host) is not None
           
""" Custom Exceptions """
class InvalidConfig(Exception):
  pass