#!/usr/bin/env node

var irc = require('./');
var request = require("request");
var fs = require('fs');

var botName = 'dad';
var bot = new irc.Client('localhost', botName, {
    debug: true,
    channels: ['#main']
});

nameTriggers = [
    new RegExp(/(^|\W+)dad(dy|a)?($|\W+|,)/i),
    new RegExp(/(^|\W+)father($|\W+|,)/i),
    new RegExp(/(^|\W+)(pop){1,2}(s)?($|\W+|,)/i),
    new RegExp(/(^|\W+)(pa){1,2}($|\W+|,)/i)
];

hiImDadTriggers = [
    new RegExp(/(^|\W+)i(')?m .*$/i)
];

var timeStamp = [];

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

// Sends message to channel and saves time stamp to determine need for throttling.
function send (to, message) {
    time = Date.now();
    var numMessages = 10;
    var messageRate = 60000; // miliseconds

    if (timeStamp.length == numMessages && time - timeStamp[0] >= messageRate
        || timeStamp.length < numMessages) {
        bot.say(to, message);
        timeStamp.push(time);
        if (timeStamp.length > numMessages) {
            timeStamp.shift();
        }
    }
}

bot.addListener('error', function(message) {
    console.error('ERROR: %s: %s', message.command, message.args.join(' '));
});

bot.addListener('message#blah', function(from, message) {
    console.log('<%s> %s', from, message);
});

bot.addListener('message', function(from, to, message) {
    console.log('%s => %s: %s', from, to, message);

	// TODO Add good morning response
	// TODO When someone says bye dad, respond with "bye [name], I love you."
	// TODO When someone says thanks dad, respond with "I'm here all day" or something like that.
    // TODO make dad sad whenever someone (or just me) leaves
	// TODO add quotes from Calvin and Hobbes
	// TODO "dad, noahsiano isn't letting me vote" do something to respond to things like this
	// TODO If someone says I'm a ..., take out the 'a' as well in the response
	// TODO when he quits it should say "Went to buy a pack of cigs and never came back"
    // TODO move bot names and ip to shared file
    // TODO add script to start both bots
	
    if (testRegexList(nameTriggers, message) && message.match(/\?$/i)) {
        send(to, "Ask your mother.");
    }
    // Hi _____, I'm dad
    else if (testRegexList(hiImDadTriggers, message)) {
        var m = message.split(/(^|\W+)i(')?m\W+/i);
        var d = m[m.length - 1].trim().split(' ');
        // Trigger a different message if someone says they're dad
        if (d.length == 1 && testRegexList(nameTriggers, d)){
            setTimeout(function() { send(to, "mmmmmmm") }, 250);
            setTimeout(function() { send(to, "no") }, 750);
        }
        else {
            send(to, 'Hi ' + m[m.length - 1].trim().replace('.', '').replace('?', '') + ', I\'m dad', true);
        }
    }
    // Just saying dad's name(s) (ignore if from mom)
    else if (testRegexList(nameTriggers, message) && from != "mom") {
        var jokeArray = fs.readFileSync('dadJokes.txt').toString().split("\n");
        var randomInt = Math.floor(Math.random() * (jokeArray.length));
        console.log(randomInt);
        var line_one = jokeArray[randomInt].split('~')[0];
        var line_two = jokeArray[randomInt].split('~')[1];
        send(to, line_one);
        // Pause for dramatic effect
        setTimeout(function() { send(to, line_two) }, 4000);
    }
    else if (message.match(/(^|\W+)awoo\?($|\W+)/i)){
        send(to, "awoo")
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
    if (who != botName) {
        send(channel, "Welcome back, " + who + "!");
    }
});
bot.addListener('part', function(channel, who, reason) {
    console.log('%s has left %s: %s', who, channel, reason);
});
bot.addListener('kick', function(channel, who, by, reason) {
    console.log('%s was kicked from %s by %s: %s', who, channel, by, reason);
});
