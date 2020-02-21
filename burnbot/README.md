# Burn Bot

### A simple IRC bot that issues burns to whomever you chose (within reason) :^)

## Prerequisites:
	
	python >=3.6

	pip 

	make


## Setup:


 1.   git clone https://github.com/AFTERWAKE/IRCBots.git

 2.   cd IRCBots/burnbot

 3.   make install

 4.   Edit ```config.yaml``` to configure the bot (see config section below)

 5.   make run



## Config
	
	serv_ip: The IP or web address of your IRC server (ex. coop.test.dyanetics.com)

	serv_port: The port the bot will use to connect to the server

	channel: The channel you want your bot in (ex. #main)

	owner (not owner_name): Your computer name (ex. cn-vm-developer.shrug.com) (could also be an actual ip)

	nickname: name given to the bot


## Admin Commands
	
	burnbot, ignore <user_name>
	burnbot, unignore <user_name>
	burnbot, say <your_message>
	burnbot, burn <anything_you_want>