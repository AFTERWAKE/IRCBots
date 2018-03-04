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

var Dad bool

// Dbot is the global variable that primarily allows for the config information
// to be smoothly passed around and updated properly.
var Dbot DadConfig
var Irc IRCBot
var Mbot MomConfig
var ircConfigFile = "irc_config.json"
var dadConfigFile = "dad_config.json"
var momConfigFile = "mom_config.json"

// UserTrigger is for all non-admin users.
var UserTrigger = hbot.Trigger{
	func(bot *hbot.Bot, m *hbot.Message) bool {
		return (m.From != Irc.Conf.Admin)
	},
	func(bot *hbot.Bot, m *hbot.Message) bool {
		PerformReply(bot, m, false)
		return false
	},
}

// AdminTrigger is for the admin user. If no admin response is performed,
// a user reponse is attempted.
var AdminTrigger = hbot.Trigger{
	func(bot *hbot.Bot, m *hbot.Message) bool {
		return (m.From == Irc.Conf.Admin)
	},
	func(bot *hbot.Bot, m *hbot.Message) bool {
		responded := PerformReply(bot, m, true)
		if !responded {
			PerformReply(bot, m, false)
		}
		return false
	},
}

// Run starts an instance of the bot, with variable dad indicating whether
// the bot should behave like a dad or a mom
func Run(dad bool) {
	Dad = dad
	var nickStr string
	rand.Seed(time.Now().Unix())
	flag.Parse()
	Irc.Conf, Dbot, Mbot = ReadConfig()
	if Dad {
		nickStr = Dbot.Name
	} else {
		nickStr = Mbot.Name
	}
	serv := flag.String("server", Irc.Conf.IP+
		":6667", "hostname and port for irc server to connect to")
	nick := flag.String("nick", nickStr, "nickname for the bot")

	hijackSession := func(bot *hbot.Bot) {
		bot.HijackSession = false
	}
	channels := func(bot *hbot.Bot) {
		if Dad {
			bot.Channels = Dbot.Channels
		} else {
			bot.Channels = Mbot.Channels
		}
	}
	bot, err := hbot.NewBot(*serv, *nick, hijackSession, channels)
	Irc.Bot = bot
	checkErr(err)
	Irc.Bot.AddTrigger(UserTrigger)
	Irc.Bot.AddTrigger(AdminTrigger)
	Irc.Bot.Logger.SetHandler(log.StdoutHandler)
	// Start up bot (this blocks until we disconnect)
	Irc.Bot.Run()
	fmt.Println("Bot shutting down.")
}
