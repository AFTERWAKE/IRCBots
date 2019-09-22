package bot

import "strings"

type Variable struct {
	Name        string   `json:"name"`
	Patterns    []Regex  `json:"patterns"`
	Description []string `json:"description"`
	Value       string   `json:"value"`
}

func (b Variable) Match(test string, botVars []Variable, depth int) (bool, string) {
	for _, pattern := range b.Patterns {
		match, substr := pattern.Match(test, botVars, depth+1)
		b.Value = strings.Replace(test, substr, "", 1)
		if match {
			return true, substr
		}
	}
	return false, test
}
