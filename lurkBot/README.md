Lurk Bot!
=============

A bot that hides in the shadows and steals usernames for fun.

Setup
-----

Prerequisites:

* Twisted (pip install Twisted)

1) `git clone https://github.com/AFTERWAKE/IRCBots.git`

2) `cd IRCBots/lurkBot;`

3) `pip install Twisted`

4) Edit lurkBot.py to configure the bot (see config section below)

5) run `python lurkBot.py` to start the bot

Config
------

serv_ip: The IP or web address of your IRC server

chatroom: The channel you want your bot in

admin: The IP(s) of the admin user. Format is a list of strings.


Twisted Documentation
---------------

http://twistedmatrix.com/documents/current/api/twisted.words.protocols.irc.IRC.html
