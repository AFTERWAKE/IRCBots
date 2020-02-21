artBot
======

A simple IRC bot that sends out ASCII paintings on the Art channel. A message is also sent out during lunchtime and break. All of this comes along with a calming quote from the one and only Bob Ross.

Dependencies
------------

* Twisted (python)

Commands
--------

* artBot, help: Shows the available commands
* artBot, paint `<`tag`>`: Paint ASCII message by its corresponding tag (random by default)
* artBot, list: Lists all of the valid message tags for painting

Config
------

* Nick: Nickname of the bot
* Admin: Administrator of the bot
* Channel: Server channel
* Server: URL that the bot connects to

To Do
-----

* Add more ASCII messages
* Add function to escape characters in JSON file
