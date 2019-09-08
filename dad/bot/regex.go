package bot

import (
	"regexp"
	"strings"
)

type Regex struct {
	Pattern []string `json:"pattern"`
}

func (b Regex) Match(test string, botVars []Variable) bool {
	return b.matchRec(test, botVars, 0)
}

func (b Regex) matchRec(test string, botVars []Variable, index int) bool {
	if index >= len(b.Pattern) {
		return test == ""
	}
	p := b.Pattern[index]
	if isCaptureVar(p) {
		// find which regex it matches
		/**
		1. Find the correct variable
		2. Find the first match in the regex array (b.Match) or return false
		3. Store the match in local memory (??)
		3. Call matchRec with substring
		*/
		panic("not yet supported")
	} else if isRegexVar(p) {
		/**
		1. Find the correct variable
		2. Find the first match in the regex array (b.Match) or return false
		3. Call matchRec with substring
		*/
		panic("not yet supported")
	} else {
		r, _ := regexp.Compile(p)
		matchIndex := r.FindStringIndex(test)
		if matchIndex == nil {
			return false
		}
		substr := strings.Replace(test, test[matchIndex[0]:matchIndex[1]], "", 1)
		return b.matchRec(substr, botVars, index+1)
	}
}
