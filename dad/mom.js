#!/usr/bin/env node

var irc = require('./');

var res = require('./lib/response.js');
var testMessage = res.testMessage;

var conf = require('./config.json');
var speak = conf.speak;

var bot = new irc.Client(conf.ip, conf.momName, {
    debug: conf.debug,
    channels: conf.channels
});

bot.addListener('error', function(message) {
    console.error('ERROR: %s: %s', message.command, message.args.join(' '));
});

bot.addListener('message#blah', function(from, message) {
    console.log('<%s> %s', from, message);
});

bot.addListener('message', function(from, to, message) {
    console.log('%s => %s: %s', from, to, message);
    var throttled = from != conf.admin;

    if (testMessage(speak.momName.regex, from, to, message) && testMessage(speak.question.regex, from, to, message)) {
        bot.say(to, speak.momName.responses.ask, throttled);
    }
});
bot.addListener('pm', function(nick, message) {
    console.log('Got private message from %s: %s', nick, message);
});
bot.addListener('join', function(channel, who) {
    console.log('%s has joined %s', who, channel);
});
bot.addListener('part', function(channel, who, reason) {
    console.log('%s has left %s: %s', who, channel, reason);
});
bot.addListener('kick', function(channel, who, by, reason) {
    console.log('%s was kicked from %s by %s: %s', who, channel, by, reason);
});
