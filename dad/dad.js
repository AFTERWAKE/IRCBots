#!/usr/bin/env node

var irc = require('./');
var request = require("request");
var fs = require('fs');

var re = require('./lib/regex.js');
var testRegexList = re.testRegexList;
var nameTriggers = re.dadNameTriggers;
var hiImDadTriggers = re.hiImDadTriggers;
var goodMorning = re.goodMorning;
var goodBye = re.goodBye;

var conf = require('./lib/config.js');

var bot = new irc.Client(conf.ip, conf.dadName, {
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

	// TODO When someone says thanks dad, respond with "I'm here all day" or something like that.
    // TODO make dad sad whenever someone (or just me) leaves
	// TODO add quotes from Calvin and Hobbes
	// TODO "dad, noahsiano isn't letting me vote" do something to respond to things like this
    // TODO get mad when people start flooding him, perhaps even leave the channel:
        // Should I really give people a reason to flood him?
    // TODO when he quits it should say "Went to buy a pack of cigs and never came back"
    // TODO require password along with admin commands, in git-ignored file
	// TODO add responses to object that also contains regex


    if (testRegexList(nameTriggers, message) && message.match(/\?$/i)) {
        bot.say(to, "Ask your mother.");
    }
    // Hi _____, I'm dad
    else if (testRegexList(hiImDadTriggers, message)) {
        var m = message.split(/(^|\W+)i(')?m\W+/i);
        var d = m[m.length - 1].trim().split(' ');
        // Trigger a different message if someone says they're dad
        if (d.length == 1 && testRegexList(nameTriggers, d)){
            setTimeout(function() { bot.say(to, "mmmmmmm", true) }, 250);
            setTimeout(function() { bot.say(to, "no", true) }, 750);
        }
        else {
            removeARegex = /^\s*(a|an)\W+/i;
            if (m[m.length - 1].match(removeARegex)) {
                m = m[m.length - 1].split(removeARegex);
            }
            bot.say(to, 'Hi ' + m[m.length - 1].trim().replace('.', '').replace('?', '') + ', I\'m dad');
        }
    }
    else if (testRegexList(nameTriggers, message)) {
        if (testRegexList(goodMorning, message)) {
            bot.say(to, "good morning " + from + "!");
        }
        else if (testRegexList(goodBye, message)) {
            bot.say(to, "bye " + from + ", I love you!");
        }
    }
    // Just saying dad's name(s) (ignore if from mom)
    else if (testRegexList(nameTriggers, message) && from != "mom") {
        var jokeArray = fs.readFileSync('dadJokes.txt').toString().split("\n");
        var randomInt = Math.floor(Math.random() * (jokeArray.length));
        console.log(randomInt);
        var line_one = jokeArray[randomInt].split('~')[0];
        var line_two = jokeArray[randomInt].split('~')[1];
        bot.say(to, line_one, true);
        // Pause for dramatic effect
        setTimeout(function() { bot.say(to, line_two, true) }, 4000);
    }
    else if (message.match(/(^|\W+)awoo\?($|\W+)/i)){
        bot.say(to, "awoo")
    }
    else {
        // private message
        console.log('private message');
    }
});
bot.addListener('pm', function(nick, message) {
    console.log('Got private message from %s: %s', nick, message);
});
bot.addListener('join', function(channel, who) {
    console.log('%s has joined %s', who, channel);
    if (who != conf.dadName) {
        bot.say(channel, "Welcome back, " + who + "!");
    }
});
bot.addListener('part', function(channel, who, reason) {
    console.log('%s has left %s: %s', who, channel, reason);
});
bot.addListener('kick', function(channel, who, by, reason) {
    console.log('%s was kicked from %s by %s: %s', who, channel, by, reason);
});