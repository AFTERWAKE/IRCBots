package bot

type Bot struct {
	Nick      []string   `json:"nick"`
	Variables []Variable `json:"variables"`
	Commands  []Command  `json:"commands"`
}

func (b Bot) MatchCommand(test string) bool {
	return false
}
