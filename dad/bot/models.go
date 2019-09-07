package bot

import (
	"github.com/whyrusleeping/hellabot"
)

type Action interface {
	PerformReply()
}

type BotVariable struct {
	Variable string `json:"variable"`
	Description []string `json:"description"`
	Regex []BotRegex `json:"regex"`
	Value string `json:"value"`
}

// Split the string into (a) the matching variable and (b) the rest of the string
func (b BotVariable) parse() []string {
	return []string {}
}

type BotRegex struct {
	Pattern []string `json:"pattern"`
}

// Parse each element in the pattern and return true if all match
func (b BotRegex) parse() bool {
	return false
}

type BotResponse struct {
	Response []string `json:"response"`
	Actions []BotAction `json:"actions"`
}

// Parse and return response
func (b BotResponse) getResponse() string {
	return ""
}

// Execute all actions
func (b BotResponse) performActions() {

}

type BotAction struct {
	Action string `json:"action"`
	Parameters []string `json:"parameters"`
}

// Execute action
func (b BotAction) performAction() {

}

type BotCommand struct {
	Variables []BotVariable `json:"variables"`
	Regex []BotRegex `json:"regex"`
	Help Help `json:"help"`
	Permissions []string `json:"permissions"`
	Responses []BotResponse `json:"responses"`
}

// Return true if message matches command regex
func (b BotCommand) isMatched(message *hbot.Message) bool {
	return false
}

func (b BotCommand) getHelp() string {
	return ""
}

func (b BotCommand) getResponse() string {
	return ""
}

func (b BotCommand) performActions() {

}

type BotConfig struct {
	Nick []string `json:"nick"`
	Variables []BotVariable `json:"variables"`
	Commands []BotCommand `json:"commands"`
}