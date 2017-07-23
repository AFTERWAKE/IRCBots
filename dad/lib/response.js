// response.js
// ========

var configFile = "config.json";

var fs = require('fs');
var conf = require("../" + configFile);
var speak = conf.speak;

exports.testMessage = testMessage;
exports.adminCommand = adminCommand;
exports.userCommand = userCommand;

function testMessage (regexList, from, to, message) {
    match = false;
    if (from.split(' ').length > 1) {
        console.error("ERROR: forgot to include who the message was from");
        return match;
    }
	if (conf.ignore.includes(from))
	{
		console.log("Ignoring message from %s", from);
		return match;
	}
    regexList.forEach(function( regex ) {
        // console.log(regex, RegExp(regex, 'i').test(message));
        if (RegExp(regex, 'i').test(message)) {
            match = true;
        }
    });
    return match;
};

function userCommand (bot, from, to, message) {
    // Limit responses to anyone who is not admin
    var throttle = from != conf.admin;
    if (bot.nick == conf.dadName) {
        userCommandDad(bot, from, to, message, throttle);
    }
    else if (bot.nick == conf.momName) {
        userCommandMom(bot, from, to, message, throttle);
    }
}

function adminCommand (bot, from, to, message) {
    throttle = from != conf.admin;
    if (to == bot.nick) {
        to = conf.channels[0];
    }
    if (testMessage(speak.ignore.regex, from, to, message)) {
        var temp = message.split(speak.ignore.regex);
        var who = temp[temp.length - 1];
        var before = conf.ignore.length;
        console.log("requested ignore for " + who);
        conf.ignore.push(who);
        if (before < conf.ignore.length) {
            console.log("Now ignoring " + who);
            updateConfig();
        }
    }
    else if (testMessage(speak.listen.regex, from, to, message)) {
        var temp = message.split(speak.listen.regex);
        var who = temp[temp.length - 1];
        console.log("requested listen for " + who);
        for (var i = 0; i < conf.ignore.length; i++) {
            if (conf.ignore[i] == who) {
                conf.ignore.splice(i, i);
                console.log("Now listening to " + who);
                updateConfig();
            }
        }
    }
    else if (testMessage(speak.say.regex, from, to, message)) {
        var temp = message.split(speak.say.regex);
        var say = temp[temp.length - 1];
        console.log("requested say " + say);
        bot.say(to, say, throttle);
    }
    else {
        userCommand(bot, from, to, message);
    }
}

function userCommandDad(bot, from, to, message, throttle) {
    // Hi _____, I'm dad
    if (testMessage(speak.hiImDad.regex, from, to, message)) {
        var m = message.split(/(^\s*i'?m\s+)/i);
        var d = m[m.length - 1].trim().split(' ');
        // Trigger a different message if someone says they're dad
        if (d.length == 1 && testMessage(speak.dadName.regex, from, to, d)){
            bot.say(to, speak.hiImDad.responses.deny, throttle);
        }
        else {
            removeARegex = /^\s*(a|an)\s+/i;
            if (m[m.length - 1].match(removeARegex)) {
                m = m[m.length - 1].split(removeARegex);
            }
            var hiImDadFiller = m[m.length - 1].trim().replace(/(\W+$)/i, '');
            bot.say(to, getLine(speak.hiImDad.responses.normal, hiImDadFiller), throttle);
        }
    }
    // Anything associated with dad's name
    else if (testMessage(speak.dadName.regex, from, to, message)) {
        // List ignored users
        if (testMessage(speak.ignored.regex, from, to, message)) {
            bot.say(conf.channels[0], "Here is a list of ignored users: ", throttle);
            bot.say(conf.channels[0], conf.ignore.toString().replace(/,/g, ', '), throttle);
        }
        // Good morning
        else if (testMessage(speak.goodMorning.regex, from, to, message)) {
            bot.say(to, getLine(speak.goodMorning.responses.normal, from), throttle);
        }
        // Ask a question
        else if (testMessage(speak.question.regex, from, to, message)) {
            bot.say(to, speak.dadName.responses.ask, throttle);            
        }
        // Just saying dad's name(s) (ignore if from mom)
        else if (from != conf.momName) {
            bot.say(to, getLine(speak.dadName.responses.joke), throttle);
        }
    }
}

function userCommandMom(bot, from, to, message, throttle) {
    if (testMessage(speak.momName.regex, from, to, message) && 
             testMessage(speak.question.regex, from, to, message)) {
        bot.say(to, speak.momName.responses.ask, throttle);
    }
}

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

function updateConfig () {
    fs.writeFile("./" + "config.json", JSON.stringify(conf, null, 4), (err) => {
        if (err) {
            console.error(err);
            return;
        }
        console.log("Config updated");
    });
}