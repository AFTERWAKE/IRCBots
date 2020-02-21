package main

import (
	"github.com/AFTERWAKE/IRCBots/dad/dadbot"
)

func main() {
	dad.Irc.Run("irc_config.json", "dad_config.json", "muted_list.json")
}
