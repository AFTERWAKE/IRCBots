High Five Bot
=============

[![Build Status](https://travis-ci.org/cadecairos/highfivebot.png?branch=master)](https://travis-ci.org/cadecairos/highfivebot)

A node bot for giving out highfives to lonely people (OR AWESOME PEOPLE!)

Setup
-----

Prerequisites:

* Node > v0.8.23
* NPM > v1.2.10

1) `git clone https://github.com/cadecairos/highfivebot.git`

2) `cd highfivebot;`

3) `npm install`

4) `cp env.dist .env`

5) Edit the .env file to configure the bot (see confic section below)

6) run `node app` to start the bot

Config
------

HOST: The URL of the IRC server

NICK: The nick of the bot

CHANNELS: A comma delimited string of channels. channels can be optionally prefixed with '#'


Troubleshooting
---------------

If `npm install` is not working, [install nvm](https://github.com/creationix/nvm#installation) and run the command `nvm install 0.8.23` to use the older version of node and npm.
