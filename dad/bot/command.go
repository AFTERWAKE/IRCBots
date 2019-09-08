package bot

import (
	hbot "github.com/whyrusleeping/hellabot"
)

type Command struct {
	Variables   []Variable `json:"variables"`
	Regex       []Regex    `json:"regex"`
	Help        Help       `json:"help"`
	Permissions []string   `json:"permissions"`
	Responses   []Response `json:"responses"`
}

// Return true if message matches command regex
func (b Command) Match(message *hbot.Message, botVars []Variable) bool {
	allVars := append(b.Variables, botVars...)
	for _, regex := range b.Regex {
		if regex.Match(message.Content, allVars) { // TODO This should probably return captured variables
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
