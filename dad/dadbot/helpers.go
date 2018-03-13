package dad

import (
	"encoding/json"
	"fmt"
	"math"
	"math/rand"
	"net/http"
	"regexp"
	"strings"
	"time"

	"github.com/whyrusleeping/hellabot"
	log "gopkg.in/inconshreveable/log15.v2"
)

// AddArticle prepands the given string with an "a" or "an" based on the first word and
// returns the result
func AddArticle(s string) string {
	for _, vowel := range []string{"a", "e", "i", "o", "u"} {
		if strings.Contains(vowel, string(s[0])) {
			return "an " + s
		}
	}
	return "a " + s
}

// GetChannelTargetOrDefault looks for a "#channel:" or "user:" in the passed msg.
// If found, it's split from the message and returned as the new destination,
// alongside the rest of the message. If not found, the original destination
// (to) and msg is returned
func GetChannelTargetOrDefault(to, msg string) (string, string) {
	channel := regexp.MustCompile("(?i)^#?\\S*:")
	if channel.MatchString(msg) {
		split := strings.SplitN(msg, ": ", 2)
		if len(split) == 2 {
			return split[0], split[1]
		} else {
			return to, msg
		}
	} else {
		return to, msg
	}
}

// GetRandomResponse chooses a random response among all within the
// given speak data. It returns a reference to the response it chose. 
func (speak *SpeakData) GetRandomResponse() *Response {
	chosenIndex := rand.Intn(len(speak.Responses))
	return &speak.Responses[chosenIndex]
}

// GetRandomLeastUsedResponse chooses a random response among all
// within the given speak data, giving priority to responses that have not
// yet been used as much. It returns a reference to the response it chose
func (speak *SpeakData) GetRandomLeastUsedResponse() *Response {
	var minCount = math.MaxUint32
	chosenIndex := rand.Intn(len(speak.Responses))
	for _, response := range speak.Responses {
		if response.Count < minCount {
			minCount = response.Count
		}
	}
	for speak.Responses[chosenIndex].Count > minCount {
		chosenIndex = rand.Intn(len(speak.Responses))
	}
	// log.Debug(fmt.Sprintf("Chosen response %d : %s", chosenIndex, speak.Responses[chosenIndex].Message))
	return &speak.Responses[chosenIndex]
}

// GetICanHazDadJoke sends an HTTP request to https://icanhazdadjoke.com
// and returns a parsed string of the joke
func GetICanHazDadJoke() string {
	url := "https://icanhazdadjoke.com/"
	client := &http.Client{}
	req, err := http.NewRequest("GET", url, nil)
	checkErr(err)
	req.Header.Set("Accept", "application/json")
	resp, err := client.Do(req)
	checkErr(err)
	decoder := json.NewDecoder(resp.Body)
	joke := ICanHazDadJoke{}
	err = decoder.Decode(&joke)
	checkErr(err)
	log.Debug(fmt.Sprintf("Got joke from icanhazdadjoke.com!"))
	r := regexp.MustCompile("(?i)\\?\\s")
	joke.Joke = r.ReplaceAllLiteralString(joke.Joke, "?\n")
	r = regexp.MustCompile("(?i)\\.\\s")
	joke.Joke = r.ReplaceAllLiteralString(joke.Joke, ".\n")
	return joke.Joke
}

// HandleTextReplacement determines what to do with each flag in a response
// #a indicates an article "a" or "an"
// #c indicates a response generated from an action handler
// #u indicates the name of the user who sent the trigger message
// #v indicates the string captured by the Variable regex
// Other conditionals can be added here. A string with all flags replaced is
// returned.
func HandleTextReplacement(message *hbot.Message, response *Response, variable string) string {
	handledMessage := response.Message
	if strings.Contains(handledMessage, "#a") {
		// TODO this will probably need to return just the correct article at some point
		variable = AddArticle(variable)
		handledMessage = strings.Replace(handledMessage, "#a ", "", -1)
	}
	if strings.Contains(handledMessage, "#c") {
		handledMessage = strings.Replace(handledMessage, "#c", variable, -1)
	}
	if strings.Contains(handledMessage, "#u") {
		handledMessage = strings.Replace(handledMessage, "#u", message.From, -1)
	}
	if strings.Contains(handledMessage, "#v") {
		handledMessage = strings.Replace(handledMessage, "#v", variable, -1)
	}
	return handledMessage
}

// MessageRateMet checks whether or not enough time has passed since the Last
// reply was sent. If the message just sent was from an admin, ignore
// time passed.
func (ib *IRCBot) MessageRateMet(message *hbot.Message) bool {
	return (time.Since(ib.LastReply.Sent) > (time.Duration(ib.IRCConfig.MessageRate)*time.Second) || message.From == ib.IRCConfig.Admin)
}

// StringInSlice checks slice s for string a and returns the first matching
// index, and -1 otherwise
func StringInSlice(a string, s []string) int {
	for i, b := range s {
		if a == b {
			return i
		}
	}
	return -1
}

// TODO stop using?
func (ib *IRCBot) getSpeakData(adminSpeak bool, sIndex int) *SpeakData {
	if adminSpeak {
		return &ib.BotConfig.AdminSpeak[sIndex]
	} else {
		return &ib.BotConfig.Speak[sIndex]
	}
}

func checkErr(err error) {
	if err != nil {
		panic(err)
	}
}
