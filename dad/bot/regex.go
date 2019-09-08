package bot

import (
	"regexp"
	"strings"
)

type Regex struct {
	Pattern []string `json:"pattern"`
}

func (b Regex) Match(test string) bool {
	return b.matchRec(test, 0)
}

func (b Regex) matchRec(test string, index int) bool {
	if index >= len(b.Pattern) {
		return test == ""
	}
	p := b.Pattern[index]
	if isCaptureVar(p) {
		panic("not yet supported")
	} else if isRegexVar(p) {
		panic("not yet supported")
	} else {
		r, _ := regexp.Compile(p)
		matchIndex := r.FindStringIndex(test)
		if matchIndex == nil {
			return false
		}
		substr := strings.Replace(test, test[matchIndex[0]:matchIndex[1]], "", 1)
		return b.matchRec(substr, index+1)
	}
}
