package bot

import "regexp"

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

func (b Command) getResponse(matched []string) []string {
	return []string{}
}

func (b Command) performActions() {

}
