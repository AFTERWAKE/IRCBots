package bot_test

import (
	"crypto/tls"
	"github.com/sorcix/irc"
	hbot "github.com/whyrusleeping/hellabot"
	"math/rand"
	"reflect"
	"testing"
	"time"

	"github.com/AFTERWAKE/IRCBots/dad/bot"
)

var hellabot = hbot.Bot{
	Incoming:      nil,
	Logger:        nil,
	Host:          "",
	Password:      "",
	Channels:      nil,
	SSL:           false,
	SASL:          false,
	HijackSession: false,
	Nick:          "",
	ThrottleDelay: 0,
	PingTimeout:   0,
	TLSConfig:     tls.Config{},
}

var b = bot.Bot{
	Nick:     []string{"bot1", "bot2", "bot3"},
	Channels: []string{"#channel1", "#channel2", "#channel3"},
	Commands: []*bot.Command{
		&bot.Command{
			Regex: []*bot.Regex{
				{Pattern: "1"},
				{Pattern: "2"},
				{Pattern: "3"},
			},
			Responses: []*bot.Response{
				{[]string{"1"}, nil},
				{[]string{"2"}, nil},
				{[]string{"3"}, nil},
			},
			Permissions: nil,
		}, &bot.Command{
			Regex: []*bot.Regex{
				{Pattern: "4"},
			},
			Responses: []*bot.Response{
				{[]string{"5"}, nil},
			},
			Permissions: nil,
		}, &bot.Command{
			Regex: []*bot.Regex{
				{Pattern: "6"},
			},
			Responses: []*bot.Response{
				{[]string{"6"}, nil},
			},
			Permissions: nil,
		}, {
			Regex: []*bot.Regex{
				{Pattern: "say the (?P<customvar>\\w+)"},
			},
			Responses: []*bot.Response{
				{[]string{"$customvar is <$customvar>"}, nil},
			},
			Permissions: nil,
		}, &bot.Command{
			Regex: []*bot.Regex{
				{Pattern: "((?P<vowel>[aeiou]+)|(?P<consonant>[bcdfghjklmnpqrstvwxyz]+))+"},
			},
			Responses: []*bot.Response{
				{[]string{"nice", "$vowel - $consonant", "$consonant - $vowel"}, nil},
			},
			Permissions: nil,
		},
	},
}

func TestBot_GetReply(t *testing.T) {
	tables := []struct {
		message *hbot.Message
		expect  []string
	}{
		{&hbot.Message{Content: "1"}, []string{"3"}},
		{&hbot.Message{Content: "3"}, []string{"1"}},
		{&hbot.Message{Content: "6"}, []string{"6"}},
		{&hbot.Message{Content: "8"}, nil},
		{&hbot.Message{Content: "b"}, []string{"nice", " - b", "b - "}},
		{&hbot.Message{Content: "ab"}, []string{"nice", "a - b", "b - a"}},
		{&hbot.Message{Content: "abcdefghijklmnopqrstuvwxyz"}, []string{"nice", "u - vwxyz", "vwxyz - u"}},
		{&hbot.Message{Content: "say the to", To: "#main"}, []string{"to is #main"}},
		{&hbot.Message{Content: "say the content"}, []string{"content is say the content"}},
		{&hbot.Message{Content: "say the timestamp", TimeStamp: time.Date(2020, 4, 20, 4, 20, 20, 20, time.UTC)}, []string{"timestamp is 2020-04-20 04:20:20.00000002 +0000 UTC"}},
		{&hbot.Message{Content: "say the command", Message: &irc.Message{Command: "comm"}}, []string{"command is comm"}},
		{&hbot.Message{Content: "say the trailing", Message: &irc.Message{Trailing: "trail"}}, []string{"trailing is trail"}},
		{&hbot.Message{Content: "say the name", Message: &irc.Message{Prefix: &irc.Prefix{Name: "awest"}}}, []string{"name is awest"}},
		{&hbot.Message{Content: "say the user", Message: &irc.Message{Prefix: &irc.Prefix{User: "awest"}}}, []string{"user is awest"}},
		{&hbot.Message{Content: "say the host", Message: &irc.Message{Prefix: &irc.Prefix{Host: "some.site.com"}}}, []string{"host is some.site.com"}},
	}

	rand.Seed(1)
	for i, table := range tables {
		expect := b.GetReply(&hellabot, table.message)
		if !reflect.DeepEqual(expect, table.expect) {
			t.Errorf(
				"Failed [%d]: expected response: %v, got %v",
				i, table.expect, expect,
			)
		}

	}
}
