# Burn Bot

### A simple IRC bot that issues burns to whomever you chose (within reason) :^)

## Prerequisites:
	
	python 3

	pip 

	make


## Setup:


 1.   git clone https://github.com/AFTERWAKE/IRCBots.git

 2.   cd IRCBots/burnbot

 3.   make install

 4.   Edit burnbot.py to configure the bot (see config section below)

 5.   make run



## Config

	chatroom: The channel you want your bot in (ex. #main)

	serv_ip: The IP or web address of your IRC server (ex. coop.test.dyanetics.com)

	owner (not owner_name): Your computer name (ex. cn-vm-developer.shrug.com)


## Admin Commands
	
	burnbot, ignore <user_name>
	burnbot, unignore <user_name>
	burnbot, say <your_message>
	burnbot, burn <anything_you_want>