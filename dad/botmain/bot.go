package main

import "github.com/AFTERWAKE/IRCBots/dad/bot"

func main() {
	b := bot.Bot{[]string{"dad"}, []bot.Command{}}
	b.Run()
}
