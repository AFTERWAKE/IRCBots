import os
import pickle
from datetime import datetime
from re import match, search
from twisted.internet import task
from twisted.words.protocols import irc


class BotCore(irc.IRCClient, object):    
  def __init__(self):
    self._tracked = []
    self._time_triggers = []
    self._commands = {}
    self._content_triggers = []

    l = task.LoopingCall(self._check_time_triggers)
    l.start(60)
    
    self.register_command("show", "ADMIN", self.cmd_show)
    self.register_command("help", "USER", self.cmd_help)
            
  """ Public interface for derivatives/mixins """
  def register_savedata(self, savedata):
    if not isinstance(savedata, dict) and not isinstance(savedata, list):
      raise InvalidSavedata
    self._tracked.append(savedata)
    
  def register_time_trigger(self, callback, hour=None, minute=None):
    if (hour and not 0 <= hour < 24) or (minute and not 0 <= minute < 60):
      raise InvalidTime
    if not callable(callback):
      raise InvalidCallback
    self._time_triggers.append((hour, minute, callback))
          
  def register_command(self, name, type, callback):
    if not name or type not in ["ADMIN", "USER", "PM"]:
      raise InvalidCommand
    if not callable(callback):
      raise InvalidCallback
    self._commands[name] = (type, callback)
    
  def register_content_trigger(self, regex_trigger, callback, ignoreCase=False):
    if not regex_trigger:
      raise InvalidMessageTrigger
    if not callable(callback):
      raise InvalidCallback
    if ignoreCase and "(?i)" not in regex_trigger:
      regex_trigger += "(?i)"
    self._content_triggers.append((regex_trigger, callback))
    
  def is_admin(self, user):
    return user.split('@')[1] == self.admin
    
  @staticmethod
  def get_nick_from_user(user):
    return user.split('!')[0]
    
  """ Overload in derivatives/mixins if extra functionality needed (use super) """
  def show(self):
    print("Admin Commands: {}".format(self._get_commands("ADMIN")))
    print("User Commands: {}".format(self._get_commands("USER")))
    print("PM Commands: {}".format(self._get_commands("PM")))
  
  """ Override in derivatives as needed """
  def help(self):
    self.msg(self.channel, "Hello, it's me, {}.".format(self.nickname))
    
  """ Core commands for every bot """
  def cmd_show(self, caller):
    "Usage: show, prints debug data to console"
    self.show()
    
  def cmd_help(self, caller):
    "Usage: help, prints help message"
    self.help()
    
  """ Twisted method overrides """
  def connectionLost(self, reason):
    print(reason)
    self._save_data()
    super(BotCore, self).connectionLost(reason)
  
  def signedOn(self):
    self._restore_data()
    self.join(self.channel)
    
  def privmsg(self, user, channel, message):
    message = irc.stripFormatting(message)
    cmd, args = self._parse_message(channel, message)
    if cmd in self._commands:
      type, callback = self._commands[cmd]
      if self._valid_context(type, user, channel):
        nick = self.get_nick_from_user(user)
        try:
          callback(nick, *args)
        except TypeError:
          if not self._is_user_command(type, channel):
            self.msg(nick, callback.__doc__)
    else:
      for trigger, callback in self._content_triggers:
        if search(trigger, message) is not None:
          callback(user, channel, message)
    
  """ Private methods """
  def _check_time_triggers(self):
    time_now = datetime.now().time()
    for hour, minute, callback in self._time_triggers:
      if hour is None or now_time.hour == hour:
        if minute is None or now_time.minute == minute:
          callback()
    
  def _save_data(self):
    with open(self._get_save_path(), 'wb') as f:
      for savedata in self._tracked:
        pickle.dump(savedata, f, protocol=2)
      
  def _restore_data(self):
    with open(self._get_save_path(), 'rb') as f:
      for i in range(len(self._tracked)):
        if isinstance(self._tracked[i], dict):
          self._tracked[i].update(pickle.load(f))
        else:
          self._tracked[i] += pickle.load(f)
          
  def _get_save_path(self):
    return os.path.realpath(os.path.join(os.getcwd(), "BOTDATA"))
          
  def _parse_message(self, channel, message):
    message = irc.stripFormatting(message)
    if channel == self.channel and self._is_channel_command(message):
      return message.split(' ')[1], message.split(' ')[2:]
    elif channel == self.nickname:
      return message.split(' ')[0], message.split(' ')[1:]
    return None, None
    
  def _valid_context(self, type, user, channel):
    return (self._is_admin_command(type, user) or
            self._is_user_command(type, channel) or
            self._is_pm_command(type, channel))
    
  def _is_admin_command(self, type, user):
    return type == "ADMIN" and self.is_admin(user)
    
  def _is_user_command(self, type, channel):
    return type == "USER" and channel == self.channel
    
  def _is_pm_command(self, type, channel):
    return type == "PM" and channel == self.nickname
    
  def _is_channel_command(self, message):
    return match("{}[,:]?\s\w+".format(self.nickname), message)
    
""" Custom Exceptions """
class InvalidSavedata(Exception):
  pass
  
class InvalidCommand(Exception):
  pass
  
class InvalidCallback(Exception):
  pass
  
class InvalidTime(Exception):
  pass
  
class InvalidMessageTrigger(Exception):
  pass