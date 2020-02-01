package bot

import (
	"flag"
	"fmt"
	hbot "github.com/whyrusleeping/hellabot"
	"math/rand"
	"time"
)

type Bot struct {
	Nick     []string  `json:"nick"`
	Channels []string  `json:"channels"`
	Commands []Command `json:"commands"`
}

func (b Bot) MatchCommand(test string) bool {
	return false
}

func (b Bot) Run() {
	rand.Seed(time.Now().Unix())
	flag.Parse()

	hijackSession := func(bot *hbot.Bot) {
		bot.HijackSession = false
	}
	channels := func(bot *hbot.Bot) {
		bot.Channels = []string{"#rents"}
	}

	// UserTrigger is for all non-admin users.
	UserTrigger := hbot.Trigger{
		Condition: func(bot *hbot.Bot, m *hbot.Message) bool {
			return true
		},
		Action: func(bot *hbot.Bot, m *hbot.Message) bool {
			println(fmt.Sprintf("%+v", m))
			if m.To == "#rents" && m.From == "awest" {
				bot.Reply(m, m.Content)
			}
			return false
		},
	}

	bot, _ := hbot.NewBot("localhost:6667", "dad", hijackSession, channels)
	bot.AddTrigger(UserTrigger)

	bot.Run()
}
