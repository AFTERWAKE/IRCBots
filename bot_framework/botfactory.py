from re import match
from twisted.internet import protocol

class BotFactory(protocol.ClientFactory, object):
  def __init__(self, bot):
    self.bot = bot
    
  def startedConnecting(self, connector):
    self.bot.cmd_restore()
    super(BotFactory, self).startedConnecting(connector)
    
  def clientConnectionLost(self, connector, reason):
    self.bot.cmd_save()
    print(reason)
    super(BotFactory, self).clientConnectionLost(connector, reason)

  def clientConnectionFailed(self, connector, reason):
    self.bot.cmd_save()
    print(reason)
    super(BotFactory, self).clientConnectionFailed(connector, reason)
    
  def set_bot_config(self, nick, channel, admin):
    self.bot.nickname = nick
    self.bot.channel = channel
    self.bot.admin = admin
    
  def buildProtocol(self, addr):
    try:
      self._validate_bot_config()
    except InvalidConfig:
      return None
    else:
      self.bot.factory = self
      return self.bot
    
  def _validate_bot_config(self):
    if not self._valid_nick(self.bot.nickname):
      print("Invalid nick provided. Must be from 1 to 9 characters. "
        "The first character cannot be a digit or a dash.")
      raise InvalidConfig
    if not self._valid_channel(self.bot.channel):
      print("Invalid channel provided. Must be in the form [#|&]<name>. "
              "Cannot have spaces, commas, or semicolons.")
      raise InvalidConfig
    if not self._valid_admin(self.bot.admin):
      print("Invalid host provided. Must be a valid IPv4 address or domain name.")
      raise InvalidConfig
      
  # Matches 1-9 characters. First character can be a letter or special character,
  #   the others can be a letter, special character, or number.
  @staticmethod
  def _valid_nick(nick):
    return match("^[a-zA-Z_[\]{}|\\`^][\w[\]{}|\\`^-]{0,8}$", nick)
    
  # Matches any string beginning with # or & without a space, comma, or colon
  @staticmethod
  def _valid_channel(channel):
    return match("^[#|&][^\s,:]*$", channel)
      
  # Matches x.x.x.x, where x is between 0 to 255, or *.com
  @staticmethod  
  def _valid_admin(host):
    octet = "(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])"
    return match("^((\w+\.)+com|({0}\.){{3}}{0})$".format(octet), host)
           
      
class InvalidConfig(Exception):
  pass