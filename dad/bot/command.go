package bot

type Command struct {
	Regex       []*Regex    `json:"regex"`
	Responses   []*Response `json:"responses"`
	Permissions []string    `json:"permissions"`
	Help        *Help       `json:"help"`
}

// Return true if message matches command regex
func (b Command) Match(message string) []string {
	for _, regex := range b.Regex {
		match, _:= regex.Match(message)
		if match != nil {
			return match
		}
	}
	return nil
}

func (b Command) getResponse(matched []string) []string {
	return []string{}
}

func (b Command) performActions() {

}
