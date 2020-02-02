package bot

import (
	"math/rand"
	"regexp"
)

type Command struct {
	Regex       []*Regex    `json:"regex"`
	Responses   []*Response `json:"responses"`
	Permissions []string    `json:"permissions"`
}

// Return true if message matches command regex
func (b Command) Match(message string) ([]string, *regexp.Regexp) {
	for _, regex := range b.Regex {
		match, re := regex.Match(message)
		if match != nil {
			return match, re
		}
	}
	return nil, nil
}

func (b Command) Replace(message string) []string {
	response := b.GetResponse()
	match, re := b.Match(message)
	if len(match) > 0 {
		return response.ParseResponse(match, re)
	}
	return nil
}

func (b Command) GetResponse() *Response {
	chosenIndex := rand.Intn(len(b.Responses))
	return b.Responses[chosenIndex]
}
