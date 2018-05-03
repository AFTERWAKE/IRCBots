Burn Bot

A simple IRC bot that issues burns to whomever you chose (within reason) :^)

Setup

Prerequisites:

	Twisted (pip install Twisted)

	Setup

Prerequisites:

    Twisted (pip install Twisted)

 1.   git clone https://github.com/AFTERWAKE/IRCBots.git

 2.   cd IRCBots/burnbot;

 3.   pip install Twisted

 4.   Edit burnbot.py to configure the bot (see config section below)

 5.   run python burnbot.py to start the bot


	Config

chatroom: The channel you want your bot in

serv_ip: The IP or web address of your IRC server

	Admin Commands
	
burnbot, ignore <user>
burnbot, unignore <user>
burnbot, say <msg>
burnbot, burn <anything_you_want>