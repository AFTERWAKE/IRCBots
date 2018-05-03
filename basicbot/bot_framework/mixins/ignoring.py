from re import match, IGNORECASE

class Ignoring(object):
  def __init__(self):
    super(Ignoring, self).__init__()
    self._ignoreMasks = []
    
    self.register_savedata(self._ignoreMasks)
    self.register_command("ignore", "ADMIN", self.cmd_ignore)
    self.register_command("unignore", "ADMIN", self.cmd_unignore)
    
  """ Commands """ 
  def cmd_ignore(self, caller, mask):
    "Usage: ignore <mask/nick>, ignores host by mask in the form nick!uname@host, e.g. *!@*1.2.3.4"
    if not self._valid_mask(mask):
      mask = "{}!*@*".format(mask)
    try:
      self._add_ignore_mask(mask)
    except DuplicateMask:
      self.msg(caller, "Duplicate mask {}".format(mask))
    else:
      self.msg(caller, "{} added to ignore list".format(mask))
            
  def cmd_unignore(self, caller, mask):
    "Usage: unignore <mask/nick>, removes mask from ignore list"
    if not self._valid_mask(mask):
      mask = "{}!*@*".format(mask)
    try:
      self._remove_ignore_mask(mask)
    except InvalidMask:
      self.msg(caller, "Could not find mask {}".format(mask))
    else:
      self.msg(caller, "{} removed from ignore list".format(mask))
      
  """ Overloaded from BotCore """
  def show(self):
    super(Ignoring, self).show()
    print("Ignore Masks: {}".format(self._ignoreMasks))
    
  """ Twisted method overrides """
  def privmsg(self, user, channel, message):
    if not self._is_ignored(user) or self.is_admin(user):
      super(Ignoring, self).privmsg(user, channel, message)
      
  """ Private methods """    
  def _add_ignore_mask(self, mask):
    if mask in self._ignoreMasks:
      raise DuplicateMask
    self._ignoreMasks.append(mask)
    
  def _remove_ignore_mask(self, mask):
    if mask not in self._ignoreMasks:
      raise InvalidMask
    self._ignoreMasks.remove(mask)
    
  def _is_ignored(self, user):
    for mask in self._ignoreMasks:
      mask_regex = mask.replace('*', '.*')
      if match(mask_regex, user, flags=IGNORECASE) is not None:
        return True
    return False
    
  # Matches user string in the format nick!uname@host
  @staticmethod
  def _valid_mask(mask):
    return match("^(.+|\*)!(.+|\*)@(.+|\*)$", mask) is not None
    
    
""" Custom Exceptions """
class InvalidMask(Exception):
  pass
  
class DuplicateMask(Exception):
  pass