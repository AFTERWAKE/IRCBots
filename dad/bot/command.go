package bot

import (
	hbot "github.com/whyrusleeping/hellabot"
)

type Command struct {
	Regex       []Regex    `json:"regex"`
	Help        Help       `json:"help"`
	Permissions []string   `json:"permissions"`
	Responses   []Response `json:"responses"`
}

// Return true if message matches command regex
func (b Command) Match(message *hbot.Message) bool {
	for _, regex := range b.Regex {
		match := regex.Match(message.Content)
		if match != nil {
			return true
		}
	}
	return false
}

func (b Command) getHelp() string {
	return ""
}

func (b Command) getResponse() string {
	return ""
}

func (b Command) performActions() {

}
