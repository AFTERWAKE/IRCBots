#!/usr/bin/env node

var irc = require('./');

var botName = 'mom';
var bot = new irc.Client('localhost', botName, {
    debug: true,
    channels: ['#main']
});

nameTriggers = [
    new RegExp(/(^|\W+)mom(my|ma)?($|\W+|,)/i),
    new RegExp(/(^|\W+)mother($|\W+|,)/i),
    new RegExp(/(^|\W+)(ma){1,2}($|\W+|,)/i)
];

function testRegexList (regexList, message) {
    match = false;
    regexList.forEach(function( regex ) {
        // console.log(regex, regex.test(message));
        if (regex.test(message)) {
            match = true;
        }
    });
    return match;
}

bot.addListener('error', function(message) {
    console.error('ERROR: %s: %s', message.command, message.args.join(' '));
});

bot.addListener('message#blah', function(from, message) {
    console.log('<%s> %s', from, message);
});

bot.addListener('message', function(from, to, message) {
    console.log('%s => %s: %s', from, to, message);

    if (testRegexList(nameTriggers, message) && message.match(/\?$/i)) {
        bot.say(to, "Ask your father.");
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
