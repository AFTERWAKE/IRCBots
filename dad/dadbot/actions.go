package dad

import (
	"regexp"
	"strings"
)

// PerformAction evaluates the action associated with the response (speak)
// and performs any necessary actions. Any content that needs to be used in
// the response will be returned.
func (ib *IRCBot) PerformAction(reply Reply, speak *SpeakData,
	variable string) (Reply, string) {
	// Handle any included action
	// TODO Turn these into integer values like messagetype
	ground := regexp.MustCompile("(?i)^ground$")
	unground := regexp.MustCompile("(?i)^unground$")
	grounded := regexp.MustCompile("(?i)^grounded$")
	if ground.MatchString(speak.Action) {
		ib.Ground(variable)
	} else if unground.MatchString(speak.Action) {
		ib.Unground(variable)
	} else if grounded.MatchString(speak.Action) {
		variable = strings.Join(ib.Muted.Users, ", ")
	}
	return reply, variable
}

// Ground checks the list of currently grounded users and adds the name if
// it has not yet been added.
func (ib *IRCBot) Ground(name string) {
	i := StringInSlice(name, ib.Muted.Users)
	if i != -1 {
		return
	}
	ib.Muted.Users = append(ib.Muted.Users, name)
}

// Unground checks the list of grounded users for the requested name and
// removes it if it is found.
func (ib *IRCBot) Unground(name string) {
	i := StringInSlice(name, ib.Muted.Users)
	if i == -1 {
		return
	}
	ib.Muted.Users = append(ib.Muted.Users[:i], ib.Muted.Users[i+1:]...)
}
