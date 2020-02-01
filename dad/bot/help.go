package bot

// Help is an optional field in a command that provides more info about the command
type Help struct {
	Message []string `json:"message"`
	Hint    []string `json:"hint"`
}

// GetHelp returns an explanation for how to use the associated command
func (b Help) GetHelp() []string {
	// var help string;
	// for message := range b.Message {

	// }
	// for hint := range b.Hint {

	// }
	return []string{}
}
