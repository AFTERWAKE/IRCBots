package main

import (
	"math/rand"
	"time"
	"github.com/whyrusleeping/hellabot"
	log "gopkg.in/inconshreveable/log15.v2"
)

func main() {
	rand.Seed(time.Now().Unix())
	serv := "irc.noahsiano.com:6667"
	nick := "bot"

	hijackSession := func(bot *hbot.Bot) {
		bot.HijackSession = false
	}
	channels := func(bot *hbot.Bot) {
		bot.Channels = []string {"#main"}
	}
	bot, err := hbot.NewBot(serv, nick, hijackSession, channels)
	checkErr(err)
	bot.AddTrigger(hbot.Trigger{
		func(bot *hbot.Bot, m *hbot.Message) bool {
			return true
		},
		func(bot *hbot.Bot, m *hbot.Message) bool {
			println(m.Message)
			return false
		}})
	bot.Logger.SetHandler(log.StdoutHandler)
	bot.Run()
}

func checkErr(err error) {
	if err != nil {
		panic(err)
	}
}
