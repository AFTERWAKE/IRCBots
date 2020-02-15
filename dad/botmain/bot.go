package main

import (
	"github.com/AFTERWAKE/IRCBots/dad/bot"
)

func main() {
	b := bot.Bot{
		Nick:     []string{"dad"},
		Channels: []string{"#rents"},
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
					{Pattern: "say the (?P<customvar>(to|content|timestamp|command|trailing|name|user|host))"},
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
	b.Run()
}
