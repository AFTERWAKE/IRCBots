package bot

import (
	"regexp"
)

type Regex struct {
	Pattern string `json:"pattern"`
}

// Match tests the given string and returns the result of the test as well as the
// compiled regex so it may be used in the future for an Expand or Replace call.
func (b Regex) Match(test string) ([]string, *regexp.Regexp) {
	r := regexp.MustCompile(b.Pattern)
	return r.FindStringSubmatch(test), r
}

func (b Regex) Replace(message, response string) string {
	match, re := b.Match(message)
	if len(match) > 0 {
		return re.ReplaceAllString(match[0], response)
	}
	return ""
}
