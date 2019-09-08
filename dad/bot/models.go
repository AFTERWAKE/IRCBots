package bot

import (
	"github.com/whyrusleeping/hellabot"
)

type Variable struct {
	Variable    string   `json:"variable"`
	Description []string `json:"description"`
	Regex       []Regex  `json:"regex"`
	Value       string   `json:"value"`
}

// Split the string into (a) the matching variable and (b) the rest of the string
func (b Variable) parse() []string {
	return []string{}
}

type Response struct {
	Response []string `json:"response"`
	Actions  []Action `json:"actions"`
}

// Parse and return response
func (b Response) getResponse() string {
	return ""
}

// Execute all actions
func (b Response) performActions() {

}

type Action struct {
	Action     string   `json:"action"`
	Parameters []string `json:"parameters"`
}

// Execute action
func (b Action) performAction() {

}

type Command struct {
	Variables   []Variable `json:"variables"`
	Regex       []Regex    `json:"regex"`
	Help        Help       `json:"help"`
	Permissions []string   `json:"permissions"`
	Responses   []Response `json:"responses"`
}

// Return true if message matches command regex
func (b Command) isMatched(message *hbot.Message) bool {
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

type Config struct {
	Nick      []string   `json:"nick"`
	Variables []Variable `json:"variables"`
	Commands  []Command  `json:"commands"`
}
