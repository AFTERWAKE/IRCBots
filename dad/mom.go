package main

import (
	"github.com/AFTERWAKE/IRCBots/dad/dadbot"
)

func main() {
	dad.Irc.Run("irc_config.json", "mom_config.json")
}
