#!/usr/bin/env node

var irc = require('./');
var bot = require('./bot.js');
var conf = require('./config.json');

var mom = new irc.Client(conf.ip, conf.momName, {
    debug: conf.debug,
    channels: conf.channels
});

bot.manageBot(mom);