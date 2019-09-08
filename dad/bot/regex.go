package bot

import (
	"regexp"
	"strings"
)

type Regex struct {
	Pattern []string `json:"pattern"`
}

// Parse each element in the pattern and return true if all match
func (b Regex) Parse(test string) bool {
	var pattern []string

	for _, p := range b.Pattern {
		if isCaptureVar(p) {
			panic("not yet supported")
		} else if isRegexVar(p) {
			panic("not yet supported")
		} else {
			pattern = append(pattern, "something else")
		}
	}
	r, _ := regexp.Compile(strings.Join(b.Pattern[:], ""))
	return r.MatchString(test)
}