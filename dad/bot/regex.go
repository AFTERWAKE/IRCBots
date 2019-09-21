package bot

import (
	"regexp"
	"strings"
)

type Regex struct {
	Pattern []string `json:"pattern"`
}

func (b Regex) Match(test string, botVars []Variable, depth int) (bool, string) {
	match, remaining := b.matchRec(test, botVars, 0, depth)
	if depth == 0 {
		return match && remaining == "", remaining
	}
	return match, remaining
}

func (b Regex) matchRec(test string, botVars []Variable, index int, depth int) (bool, string) {
	if index >= len(b.Pattern) {
		return true, test
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
		// panic("not yet supported")
		regexVar := getVar(p, botVars)
		match, substr := regexVar.Match(test, botVars, depth+1)
		if regexVar != nil && match {
			return b.matchRec(substr, botVars, index+1, depth+1)
		}
		return false, test
	} else if isRegexVar(p) {
		/**
		1. If a match is made, we have iterated through a Regex struct in the Variable and should be left with either an empty string or what remains of the string we're trying to match (or the string we started with if the match failed)
		2. from there, do the same return step as the else block
		*/
		regexVar := getVar(p, botVars)
		match, substr := regexVar.Match(test, botVars, depth+1)
		if regexVar != nil && match {
			return b.matchRec(substr, botVars, index+1, depth+1)
		}
		return false, test
	} else {
		r := regexp.MustCompile(p)
		matchIndex := r.FindStringIndex(test)
		if matchIndex == nil {
			return false, test
		}
		substr := strings.Replace(test, test[matchIndex[0]:matchIndex[1]], "", 1)
		return b.matchRec(substr, botVars, index+1, depth+1)
	}
}
