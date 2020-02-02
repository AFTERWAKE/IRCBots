package bot

import "regexp"

type Response struct {
	Response []string `json:"response"`
	Actions  []Action `json:"actions"`
}

// Parse and return response
func (b Response) ParseResponse(match []string, re *regexp.Regexp) []string {
	if match != nil {
		resp := make([]string, len(b.Response))
		for i, line := range b.Response {
			resp[i] = re.ReplaceAllString(match[0], line)
		}
		return resp
	}
	return nil
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
