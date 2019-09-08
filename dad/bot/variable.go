package bot

type Variable struct {
	Name        string   `json:"name"`
	Patterns    []Regex  `json:"patterns"`
	Description []string `json:"description"`
	Value       string   `json:"value"`
}

// Split the string into (a) the matching variable and (b) the rest of the string
func (b Variable) parse() []string {
	return []string{}
}

func (b Variable) Match(test string) bool {
	return false
}
