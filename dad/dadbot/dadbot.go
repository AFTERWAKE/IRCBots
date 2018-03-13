// Package dad is an extension of hellabot that plays the role of an IRC
// chat bot, either as a mom or a dad
package dad

import (
	"flag"
	"fmt"
	"math/rand"
	"time"

	"github.com/whyrusleeping/hellabot"
	log "gopkg.in/inconshreveable/log15.v2"
)

// UserTrigger is for all non-admin users.
var UserTrigger = hbot.Trigger{
	func(bot *hbot.Bot, m *hbot.Message) bool {
		return (m.From != Irc.IRCConfig.Admin)
	},
	func(bot *hbot.Bot, m *hbot.Message) bool {
		Irc.PerformReply(m, false)
		return false
	},
}

// AdminTrigger is for the admin user. If no admin response is performed,
// a user reponse is attempted.
var AdminTrigger = hbot.Trigger{
	func(bot *hbot.Bot, m *hbot.Message) bool {
		return (m.From == Irc.IRCConfig.Admin)
	},
	func(bot *hbot.Bot, m *hbot.Message) bool {
		responded := Irc.PerformReply(m, true)
		if !responded {
			Irc.PerformReply(m, false)
		}
		return false
	},
}

// IRCBot is the global variable that tracks any common, constant values between
// the two bots. This is only accessed once at startup by each bot
var Irc IRCBot

// Run starts an instance of the bot, with variable dad indicating whether
// the bot should behave like a dad or a mom
func (ib *IRCBot) Run(ircConfigFileName, botConfigFileName, mutedListFileName string) {
	rand.Seed(time.Now().Unix())
	flag.Parse()
	ib.IRCConfigFile = ircConfigFileName
	ib.BotConfigFile = botConfigFileName
	ib.MutedFile = mutedListFileName
	ib.ReadConfig(ib.IRCConfigFile, ib.BotConfigFile, ib.MutedFile)
	serv := flag.String("server", ib.IRCConfig.IP+
		":6667", "hostname and port for irc server to connect to")
	nick := flag.String("nick", ib.BotConfig.Name, "nickname for the bot")

	hijackSession := func(bot *hbot.Bot) {
		bot.HijackSession = false
	}
	channels := func(bot *hbot.Bot) {
		bot.Channels = ib.BotConfig.Channels
	}
	bot, err := hbot.NewBot(*serv, *nick, hijackSession, channels)
	ib.Bot = bot
	checkErr(err)
	ib.AddTrigger(UserTrigger)
	ib.AddTrigger(AdminTrigger)
	ib.Bot.Logger.SetHandler(log.StdoutHandler)
	// Start up bot (this blocks until we disconnect)
	ib.Bot.Run()
	fmt.Println("Bot shutting down.")
}

func (ib IRCBot) AddTrigger(t hbot.Trigger) {
	ib.Bot.AddTrigger(t)
}
