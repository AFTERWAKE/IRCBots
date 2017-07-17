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

var conf = require('./config.json');
var speak = conf.speak;

var bot = new irc.Client(conf.ip, conf.dadName, {
    debug: conf.debug,
    channels: conf.channels
});

// Join line to filler and/or get random response from list
function getLine(text, fill=null) {
    var randLine = Math.floor(Math.random() * (text.length));
    // console.log(randLine);
    text = text[randLine][0];
    if (RegExp(/\[a\]/).test(text) && fill != null) {
        text = text.replace("[a]", fill);
    }
    // console.log(text);
    return text;
}

bot.addListener('error', function(message) {
    console.error('ERROR: %s: %s', message.command, message.args.join(' '));
});

bot.addListener('message#blah', function(from, message) {
    console.log('<%s> %s', from, message);
});

bot.addListener('message', function(from, to, message) {
    console.log('%s => %s: %s', from, to, message);

    // TODO make dad sad whenever someone (or just me) leaves
	// TODO "dad, noahsiano isn't letting me vote" do something to respond to things like this
    // TODO get mad when people start flooding him, perhaps even leave the channel:
        // Should I really give people a reason to flood him?
    // TODO when he quits it should say "Went to buy a pack of cigs and never came back"
    // TODO require password along with admin commands, in git-ignored file
	// TODO Add list of least favorite children (i.e. people to ignore)
	// TODO Add list of favorite children and give them special responses

    // Hi _____, I'm dad
    if (testRegexList(speak.hiImDad.regex, message)) {
        var m = message.split(/(^|\W+)i(')?m\W+/i);
        var d = m[m.length - 1].trim().split(' ');
        // Trigger a different message if someone says they're dad
        if (d.length == 1 && testRegexList(speak.dadName.regex, d)){
			bot.say(to, speak.hiImDad.responses.deny, true);
        }
        else {
            removeARegex = /^\s*(a|an)\W+/i;
            if (m[m.length - 1].match(removeARegex)) {
                m = m[m.length - 1].split(removeARegex);
            }
            var hiImDadFiller = m[m.length - 1].trim().replace('.', '').replace('?', '');
            bot.say(to, getLine(speak.hiImDad.responses.normal, hiImDadFiller), true);
        }
    }
    // Anything associated with dad's name
    else if (testRegexList(speak.dadName.regex, message)) {
        // Good morning
        if (testRegexList(speak.goodMorning.regex, message)) {
            bot.say(to, getLine(speak.goodMorning.responses.normal, from), true);
        }
        // Ask a question
        else if (testRegexList(speak.question.regex, message)) {        
            bot.say(to, speak.dadName.responses.ask, true);
        }
        // Just saying dad's name(s) (ignore if from mom)
        else if (from != conf.momName) {
            bot.say(to, getLine(speak.dadName.responses.joke), true);
        }
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
});
bot.addListener('part', function(channel, who, reason) {
    console.log('%s has left %s: %s', who, channel, reason);
});
bot.addListener('kick', function(channel, who, by, reason) {
    console.log('%s was kicked from %s by %s: %s', who, channel, by, reason);
});