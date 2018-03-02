// Package dad is an extension of hellabot that plays the role of an IRC
// chat bot, either as a mom or a dad
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

// ChooseDestination determines the target for the bot's reply
// purely based on who sent the trigger message and where they sent it
// Returns the destination
func ChooseDestination(message *hbot.Message) string {
    var to string
    if strings.Contains(message.To, "#") {
        to = message.To
    } else {
        to = message.From
    }
    return to
}

// GetRandomLeastUsedResponseIndex chooses a random response among all
// within the given speak data, giving priority to responses that have not
// yet been used as much. It returns the index of the response it chose
func GetRandomLeastUsedResponseIndex(speak SpeakData) int {
    var minCount = math.MaxUint32
    chosenIndex := rand.Intn(len(speak.Response))
    for _, response := range speak.Response {
        if response.Count < minCount {
            minCount = response.Count
        }
    }
    for speak.Response[chosenIndex].Count > minCount {
        chosenIndex = rand.Intn(len(speak.Response))
    }
    // log.Debug(fmt.Sprintf("Chosen response %d : %s", chosenIndex, speak.Response[chosenIndex].Message))
    return chosenIndex
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
func HandleTextReplacement(message *hbot.Message, response ResponseData,
    variable string) string {
    if strings.Contains(response.Message, "#a") {
        // TODO this will probably need to return just the correct article at some point
        variable = AddArticle(variable)
        response.Message = strings.Replace(response.Message, "#a ", "", -1)
    }
    if strings.Contains(response.Message, "#c") {
        response.Message = strings.Replace(response.Message, "#c", variable, -1)
    }
    if strings.Contains(response.Message, "#u") {
        response.Message = strings.Replace(response.Message, "#u", message.From, -1)
    }
    if strings.Contains(response.Message, "#v") {
        response.Message = strings.Replace(response.Message, "#v", variable, -1)
    }
    return response.Message
}

// MessageRateMet checks whether or not enough time has passed since the Last
// reply was sent. If the message just sent was from an admin, ignore
// time passed.
func MessageRateMet(message *hbot.Message) bool {
    return (time.Since(Irc.LastReply.Sent) > (time.Duration(Irc.Conf.MessageRate)*time.Second) || message.From == Irc.Conf.Admin)
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

func getSpeakData(adminSpeak bool) []SpeakData {
    var s []SpeakData
    if Dad == false {
        if adminSpeak {
            s = Mbot.AdminSpeak
        } else {
            s = Mbot.Speak
        }
    } else {
        if adminSpeak {
            s = Dbot.AdminSpeak
        } else {
            s = Dbot.Speak
        }
    }
    return s
}

func checkErr(err error) {
    if err != nil {
        panic(err)
    }
}
