package bot

type Variable struct {
	Name        string   `json:"name"`
	Patterns    []Regex  `json:"patterns"`
	Description []string `json:"description"`
	Value       string   `json:"value"`
}

func (b Variable) Match(test string, botVars []Variable) bool {
	for _, pattern := range b.Patterns {
		if pattern.Match(test, botVars) {
			return true
		}
	}
	return false
}
