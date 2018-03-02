package dad

import (
  "regexp"
  "strings"
)

// PerformAction evaluates the action associated with the response (speak)
// and performs any necessary actions. Any content that needs to be used in
// the response will be returned.
func PerformAction(reply Reply, speak SpeakData,
    variable string) (Reply, string) {
    // Handle any included action
    ground := regexp.MustCompile("(?i)^ground$")
    unground := regexp.MustCompile("(?i)^unground$")
    grounded := regexp.MustCompile("(?i)^grounded$")
    message := regexp.MustCompile("(?i)^message$")
    if ground.MatchString(speak.Action) {
        Ground(variable)
    }
    if unground.MatchString(speak.Action) {
        Unground(variable)
    }
    if grounded.MatchString(speak.Action) {
        variable = strings.Join(Dbot.Grounded, ", ")
    }
    if message.MatchString(speak.Action) {
        to, msg := FormatMessage(variable, speak)
        if len(to) > 0 {
            reply.To = to
        }
        variable = msg
    }
    return reply, variable
}

// Ground checks the list of currently grounded users and adds the name if
// it has not yet been added.
func Ground(name string) {
    i := StringInSlice(name, Dbot.Grounded)
    if i != -1 {
        return
    }
    Dbot.Grounded = append(Dbot.Grounded, name)
}

// Unground checks the list of grounded users for the requested name and
// removes it if it is found.
func Unground(name string) {
    i := StringInSlice(name, Dbot.Grounded)
    if i == -1 {
        return
    }
    Dbot.Grounded = append(Dbot.Grounded[:i], Dbot.Grounded[i+1:]...)
}

// FormatMessage splits message into its destination and message components
// (formatted as <recipient>: <rest>). It returns the recipient,
// or the bot's primary channel if a recipient was not specified,
// and the actual message
func FormatMessage(message string, s SpeakData) (string, string) {
    to := ""
    message = RemoveTriggerRegex(message, s.Regex)
    to = RemoveLiteralRegex(message, ":.*")
    if to == message {
        to = Dbot.Channels[0]
    }
    message = RemoveLiteralRegex(message, ".*:\\s")
    return to, message
}
