from bot_core import BotCore

class TestBotStub(BotCore):
  def __init__(self):
    super(TestBotStub, self).__init__()
    self.nickname = "testbot"
    self.channel = "#main"
    self.admin = "admin.com"
    
class TestBotSpy(TestBotStub):
  def __init__(self):
    super(TestBotSpy, self).__init__()
    self.output = ""
    self.register_command("admin", "ADMIN", self.cmd_admin)
    self.register_command("user", "USER", self.cmd_user)
    self.register_command("pm", "PM", self.cmd_pm)
    
  def clear_output(self):
    self.output = ""
    
  def msg(self, channel, message, length=None):
    self.output += "MSG to {}: {}".format(channel, message)
    
  def cmd_admin(self, caller):
    "Test ADMIN command"
    self.output += "ADMIN"
    
  def cmd_user(self, caller):
    "Test USER command"
    self.output += "USER"
    
  def cmd_pm(self, caller):
    "Test PM command"
    self.output += "PM"