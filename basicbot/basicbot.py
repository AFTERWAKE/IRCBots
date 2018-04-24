import pickle
from datetime import datetime
from re import match, IGNORECASE
from twisted.internet import task
from twisted.internet import protocol
from twisted.words.protocols import irc


class BasicBot(irc.IRCClient, object):    
  def __init__(self):
    self._tracked = []
    self._time_triggers = []
    self._commands = {}
    self._message_triggers = []

    l = task.LoopingCall(self._check_time_triggers)
    l.start(60)
    
    self.register_command("debug", "ADMIN", self.cmd_debug)
    self.register_command("say", "ADMIN", self.cmd_say)
    self.register_command("me", "ADMIN", self.cmd_me)
    self.register_command("quit", "ADMIN", self.cmd_quit)
    self.register_command("save", "ADMIN", self.cmd_save)
    self.register_command("restore", "ADMIN", self.cmd_restore)
    self.register_command("help", "USER", self.help)
    self.register_command("commands", "USER", self.cmd_list_commands)
    
  """ Interface for derivatives/mixins """
  # Override in mixins/add-ons to add necessary debug info as needed (use super)
  def print_debug(self):
    print("Admin Commands: {}".format([k for k in self._commands if self._commands[k][0] == "ADMIN"]))
    print("User Commands: {}".format([k for k in self._commands if self._commands[k][0] == "USER"]))
    print("PM Commands: {}".format([k for k in self._commands if self._commands[k][0] == "PM"]))
    
  # Override in derivatives for unique help message
  def help(self):
    self.msg(self.channel, "Hello, it's me, {}.".format(self.nickname))
    
  def register_savedata(self, savedata):
    self._tracked.append(savedata)
    
  def register_time_trigger(self, callback, hour=None, minute=None):
    self._time_triggers.append((hour, minute, callback))
          
  def register_command(self, name, type, callback):
    self._commands[name] = (type, callback)
    
  def register_message_trigger(self, trigger, callback):
    self._message_triggers.append((trigger, callback))
  
  """ Basic commands """
  def cmd_debug(self):
    "Usage: debug, shows all debug data"
    self.print_debug()
    
  def cmd_say(self, *words):
    "Usage: say <message>, sends message to channel"
    if words:
      self.msg(self.channel, ' '.join(words))
    else:
      raise TypeError
    
  def cmd_me(self, *words):
    "Usage: me <message>, sends action to channel"
    if words:
      self.describe(self.channel, ' '.join(words))
    else:
      raise TypeError
    
  def cmd_quit(self, *words):
    "Usage: quit [message], quits channel with optional message"
    self.quit(' '.join(words))
    
  def cmd_save(self):
    "Usage: save, saves data to file"
    try:
      self.save_data()
      print("Save successful")
    except Exception, e:
      print("Save failed: {}".format(e))
      
  def cmd_restore(self):
    "Usage: restore, restores data from file"
    try:
      self.restore_data()
      print("Restore successful")
    except Exception, e:
      print("Restore failed: {}".format(e))
      
  def cmd_help(self, user):
    "Usage: help, prints help message"
    self.help()
      
  def cmd_list_commands(self, user):
    "Usage: commands, lists available user commands"
    user_commands = [k for k in self._commands if self._commands[k][0] == "USER"]
    pm_commands = [k for k in self._commands if self._commands[k][0] == "PM"]
    if user_commands:
      self.msg(self.channel, "User Commands: {} (send in {} with bot name; e.g. {}, commands)".format(user_commands, self.channel, self.nickname))
    if pm_commands:
      self.msg(self.channel, "PM Commands: {} (send in PM to bot)".format(pm_commands))
    
  """ Utilities """
  def _check_time_triggers(self):
    now_time = datetime.now().time()
    for hour, minute, callback in self._time_triggers:
      if hour is None or now_time.hour == hour:
        if minute is None or now_time.minute == minute:
          callback()
    
  def save_data(self):
    with open("BOTDATA", 'wb') as f:
      for savedata in self._tracked:
        pickle.dump(savedata, f, protocol=2)
      
  def restore_data(self):
    with open("BOTDATA", 'rb') as f:
      for i in range(len(self._tracked)):
        if isinstance(self._tracked[i], dict):
          self._tracked[i].update(pickle.load(f))
        else:
          self._tracked[i] += pickle.load(f)
          
  def is_admin(self, user):
    return user.split('@')[1] == self.admin
    
  @staticmethod
  def get_nick_from_user(user):
    return user.split('!')[0]
    
  """ Twisted Methods """
  def signedOn(self):
    self.join(self.channel, key="testing")
    
  def privmsg(self, user, channel, message):
    message = irc.stripFormatting(message)
    cmd, args = self._parse_message(channel, message)
    if cmd in self._commands:
      type, callback = self._commands[cmd]
      try:
        if self._is_admin_command(type, user):
          callback(*args)
        else:
          callback(user, *args)
      except TypeError:
        if self._is_admin_command(type, user):
          print(callback.__doc__)
        elif self._is_pm_command(type, channel):
          self.msg(self.get_nick_from_user(user), callback.__doc__)
    else:
      for trigger, callback in self._message_triggers:
        if match(trigger, message):
          callback(user, channel, message)
        
  def _parse_message(self, channel, message):
    message = irc.stripFormatting(message)
    if channel == self.channel and self._is_channel_command(message):
      return message.split(' ')[1], message.split(' ')[2:]
    elif channel == self.nickname:
      return message.split(' ')[0], message.split(' ')[1:]
    return None, None
    
  def _is_admin_command(self, type, user):
    return type == "ADMIN" and self.is_admin(user)
    
  def _is_user_command(self, type, channel):
    return type == "USER" and channel == self.channel
    
  def _is_pm_command(self, type, channel):
    return type == "PM" and channel == self.nickname
    
  def _is_channel_command(self, message):
    return match("{}[,:]?\s\w+".format(self.nickname), message)
        
      
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