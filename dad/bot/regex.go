package bot

import (
	"regexp"
)

type Regex struct {
	Pattern string `json:"pattern"`
}

func (b Regex) Match(test string) []string {
	r := regexp.MustCompile(b.Pattern)
	return r.FindStringSubmatch(test)
}
