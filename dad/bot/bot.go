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
	Commands []*Command `json:"commands"`
}

func (b Bot) ShouldReply(bot *hbot.Bot, m *hbot.Message) bool {
	return m.To == "#rents" && m.From == "awest"
}

func (b Bot) GetReply(bot *hbot.Bot, m *hbot.Message) []string {
	for _, command := range b.Commands {
		match, re := command.Match(m.Content)
		response := command.GetResponse()
		responseText := response.ParseResponse(match, re)
		if responseText != nil {
			return responseText
		}
	}
	return nil
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
			if b.ShouldReply(bot, m) {
				reply := b.GetReply(bot, m)
				for _, r := range reply {
					bot.Reply(m, r)
				}
			}
			return false
		},
	}

	bot, _ := hbot.NewBot("localhost:6667", "dad", hijackSession, channels)
	bot.AddTrigger(UserTrigger)

	bot.Run()
}
