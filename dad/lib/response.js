// response.js
// ========

var configFile = "config.json";

var fs = require('fs');
var conf = require("../" + configFile);
var speak = conf.speak;

exports.testMessage = testMessage;
exports.adminCommand = adminCommand;

function testMessage (regexList, from, message) {
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

function adminCommand (bot, message) {
    if (testMessage(speak.ignored.regex, conf.admin, message)) {
        bot.say(conf.channels[0], "Here is a list of ignored users: ", false);
        bot.say(conf.channels[0], conf.ignore.toString().replace(/,/g, ', '), false);
    }
    else if (testMessage(speak.ignore.regex, conf.admin, message)) {
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
    else if (testMessage(speak.listen.regex, conf.admin, message)) {
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