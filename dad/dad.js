#!/usr/bin/env node

var irc = require('./');    
var bot = require('./bot.js');
var conf = require('./config.json');

var dad = new irc.Client(conf.ip, conf.dadName, {
    debug: conf.debug,
    channels: conf.channels
});

bot.manageBot(dad);