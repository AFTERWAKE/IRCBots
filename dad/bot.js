#!usr/bin/env node

var request = require("request");
var fs = require('fs');

var res = require('./lib/response.js');
var testMessage = res.testMessage;
var adminCommand = res.adminCommand;
var userCommand = res.userCommand;

var conf = require('./config.json');
var speak = conf.speak;

exports.manageBot = manageBot;

function manageBot(bot) {
    bot.addListener('error', function(message) {
        console.error('ERROR: %s: %s', message.command, message.args.join(' '));
    });

    bot.addListener('message', function(from, to, message) {
        console.log('%s => %s: %s', from, to, message);

        // TODO make dad sad whenever someone (or just me) leaves
        // TODO "dad, noahsiano isn't letting me vote" do something to respond to things like this
        // TODO get mad when people start flooding him, perhaps even leave the channel:
            // Should I really give people a reason to flood him?
        // TODO when he quits it should say "Went to buy a pack of cigs and never came back"
        // TODO require password along with admin commands, in git-ignored file
        // TODO Make multiple channels work better (i.e. remove checks involving conf.channels[0])
        // TODO Let dad talk to specific people or channels

        if (to == conf.dadName) {
            if (from == conf.admin) {
                adminCommand(bot, from, to, message);
            }
        }
        else if (to == conf.channels[0]) {
            if (from == conf.admin){
                adminCommand(bot, from, to, message);
            }
            else {
                userCommand(bot, from, to, message);
            }
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
}