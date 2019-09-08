package bot

type Response struct {
	Response []string `json:"response"`
	Actions  []Action `json:"actions"`
}

// Parse and return response
func (b Response) getResponse() string {
	return ""
}

// Execute all actions
func (b Response) performActions() {

}

type Action struct {
	Action     string   `json:"action"`
	Parameters []string `json:"parameters"`
}

// Execute action
func (b Action) performAction() {

}
