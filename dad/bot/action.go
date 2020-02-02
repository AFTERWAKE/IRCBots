package bot

type Action struct {
	Action     string   `json:"action"`
	Parameters []string `json:"parameters"`
}

// Execute action
func (b Action) performAction() {

}
