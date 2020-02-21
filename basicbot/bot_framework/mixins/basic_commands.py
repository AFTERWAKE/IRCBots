class BasicCommands(object):
  def __init__(self):
    super(BasicCommands, self).__init__()
    self.register_command("say", "ADMIN", self.cmd_say)
    self.register_command("me", "ADMIN", self.cmd_me)
    self.register_command("quit", "ADMIN", self.cmd_quit)
    self.register_command("commands", "USER", self.cmd_list_commands)
    
  """ Commands """    
  def cmd_say(self, caller, *words):
    "Usage: say <message>, sends message to channel"
    if words:
      self.msg(self.channel, ' '.join(words))
    else:
      raise TypeError
    
  def cmd_me(self, caller, *words):
    "Usage: me <message>, sends action to channel"
    if words:
      self.describe(self.channel, ' '.join(words))
    else:
      raise TypeError
    
  def cmd_quit(self, caller, *words):
    "Usage: quit [message], quits channel with optional message"
    self.quit(' '.join(words))
            
  def cmd_list_commands(self, caller):
    "Usage: commands, lists available user commands"
    user_commands = self._get_commands("USER")
    pm_commands = self._get_commands("PM")
    if user_commands:
      self.msg(self.channel, "User Commands: {} (send in {} with bot name; "
        "e.g. {}, commands)".format(user_commands, self.channel, self.nickname))
    if pm_commands:
      self.msg(self.channel, "PM Commands: {} (send in PM to bot)".format(pm_commands))
      
  """ Utilities """
  def _get_commands(self, type):
    return [k for k in self._commands if self._commands[k][0] == type]