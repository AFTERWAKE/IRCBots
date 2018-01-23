// Package dad is an extension of hellabot that plays the role of an IRC
// chat bot, either as a mom or a dad
package dad

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"math"
	"math/rand"
	"os"
	"regexp"
	"strings"
	"time"

	"github.com/whyrusleeping/hellabot"
	log "gopkg.in/inconshreveable/log15.v2"
)

// Configuration lists all the high-level content of the config file
type Configuration struct {
	Admin       string
	AdminSpeak  []SpeakData
	Channels    []string
	DadName     string
	Debug       bool
	Grounded    []string
	Ip          string
	MessageRate int // Using 1 reply per x seconds
	MomName     string
	MomSpeak    []SpeakData
	Speak       []SpeakData
	Timeout     int // Timeout between multi-lined reply
}

// SpeakData is the regex-to-response pairing for each possible response.
// There can be more than one response, and it will be chosen semi-randomly.
type SpeakData struct {
	Action		string
	Regex    	RegexData
	Response 	[]ResponseData
}

// ResponseData contains the bot's reply and the number of times the reply
// has been sent. Message may contain [...] blocks for different types of
// text replacement/manipulation.
type ResponseData struct {
	Message 	string
	Count   	int
}

// RegexData makes it a little easier to capture text by having
// regex that seperates the message content into two parts.
// The Trigger section acts as the command that the bot responds to.
// The Variable is what the bot will take and use in its response (if needed).
// If no reuse of message content is needed in a response, leave Variable blank.
type RegexData struct {
	Trigger		string
	Variable 	string
}

// Reply includes the final formatted response (all text replacement blocks
// dealt with), the destination, and the time the message was sent at.
type Reply struct {
	Content 	[]string
	To      	string
	Sent    	time.Time
}

// IRCBot is an extension of hellabot's Bot that includes an indicator for
// whether the bot is acting as mom or dad, the config information, and the
// last reply sent by the bot
type IRCBot struct {
	Bot       	*hbot.Bot
	Dad       	bool
	Conf      	Configuration
	LastReply 	Reply
}

// Dbot is the global variable that primarily allows for the config information
// to be smoothly passed around and updated properly.
var Dbot IRCBot
var configFile = "conf.json"

// Run starts an instance of the bot, with variable dad indicating whether
// the bot should behave like a dad or a mom
func Run(dad bool) {
	var nickStr string
	rand.Seed(time.Now().Unix())
	flag.Parse()
	Dbot.Conf = InitConfig()
	Dbot.Dad = dad
	if Dbot.Dad {
		nickStr = Dbot.Conf.DadName
	} else {
		nickStr = Dbot.Conf.MomName
	}
	serv := flag.String("server", Dbot.Conf.Ip+
		":6667", "hostname and port for irc server to connect to")
	nick := flag.String("nick", nickStr, "nickname for the bot")

	hijackSession := func(bot *hbot.Bot) {
		bot.HijackSession = false
	}
	channels := func(bot *hbot.Bot) {
		bot.Channels = Dbot.Conf.Channels
	}
	bot, err := hbot.NewBot(*serv, *nick, hijackSession, channels)
	Dbot.Bot = bot
	if err != nil {
		panic(err)
	}
	Dbot.Bot.AddTrigger(UserTrigger)
	Dbot.Bot.AddTrigger(AdminTrigger)
	Dbot.Bot.Logger.SetHandler(log.StdoutHandler)
	// Start up bot (this blocks until we disconnect)
	Dbot.Bot.Run()
	fmt.Println("Bot shutting down.")
}

// InitConfig returns an initialized config.
func InitConfig() Configuration {
	file, _ := os.Open(configFile)
	defer file.Close()
	decoder := json.NewDecoder(file)
	conf := Configuration{}
	err := decoder.Decode(&conf)
	if err != nil {
		panic(err)
	}
	return conf
}

// UpdateConfig parses the current config information and rewrites it to
// the config file.
func UpdateConfig() {
	jsonData, err := json.MarshalIndent(Dbot.Conf, "", "    ")
	if err != nil {
		panic(err)
	}
	ioutil.WriteFile(configFile, jsonData, 0644)
}

// Ground checks the list of currently grounded users and adds the name if
// it has not yet been added.
func Ground(name string) {
	i := StringInSlice(name, Dbot.Conf.Grounded)
	if i != -1 { return }
	Dbot.Conf.Grounded = append(Dbot.Conf.Grounded, name)
}

// Unground checks the list of grounded users for the requested name and
// removes it if it is found.
func Unground(name string) {
	i := StringInSlice(name, Dbot.Conf.Grounded)
	if i == -1 { return }
	Dbot.Conf.Grounded[len(Dbot.Conf.Grounded) - 1], Dbot.Conf.Grounded[i] =
		Dbot.Conf.Grounded[i], Dbot.Conf.Grounded[len(Dbot.Conf.Grounded) - 1]
	Dbot.Conf.Grounded = Dbot.Conf.Grounded[:len(Dbot.Conf.Grounded) - 1]
}

// TestMessage tests the passed message against the passed regex and returns
// whether or not a match was found
func TestMessage(regex RegexData, message *hbot.Message) bool {
	var substring string
	match := false
	t, v := MustCompileRegexData(regex)
	// log.Debug(fmt.Sprintf("Trigger regex matched '%s' from '%s'", t.FindString(message.Content), message.Content))

	if t.FindString(message.Content) != "" {
		match = true
	}
	if match && regex.Variable != "" {
		substring = t.ReplaceAllLiteralString(message.Content, "")
		// log.Debug(fmt.Sprintf("Variable regex matched '%s' from '%s'", v.FindString(substring), substring))
		if v.FindString(substring) == "" {
			match = false
		}
	}
	return match
}

// MessageRateMet checks whether or not enough time has passed since the Last
// reply was sent. If the message just sent was from an admin, ignore
// time passed.
func MessageRateMet(message *hbot.Message) bool {
	return (time.Since(Dbot.LastReply.Sent) > (time.Duration(Dbot.Conf.MessageRate)*time.Second) || message.From == Dbot.Conf.Admin)
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

// RemoveTriggerRegex removes Trigger matching substrings from
// the given string
// This doesn't necessarily leave behind the Variable portion, as there could
// be additional message content that matches neither the Trigger nor Variable.
func RemoveTriggerRegex(s string, regex RegexData) string {
	var substring string
	t, _ := MustCompileRegexData(regex)
	substring = t.ReplaceAllLiteralString(s, "")
	return substring
}

// GetVariableRegex returns only the part of the string that matches the
// Variable portion of RegexData
func GetVariableRegex(s string, regex RegexData) string {
	v := regexp.MustCompile(regex.Variable)
	// log.Debug(fmt.Sprintf("Variable regex matched '%s' from '%s'", v.FindString(s), s))
	return v.FindString(s)
}

// RemoveLiteralRegex removes a matching literal that is passed as regex from
// the given string, s, and returns the result.
func RemoveLiteralRegex(s string, regex string) string {
	r := regexp.MustCompile(regex)
	return r.ReplaceAllLiteralString(s, "")
}

func MustCompileRegexData(regex RegexData) (*regexp.Regexp,
											*regexp.Regexp) {
	return 	regexp.MustCompile(regex.Trigger),
			regexp.MustCompile(regex.Variable)
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
		to = Dbot.Conf.Channels[0]
	}
	message = RemoveLiteralRegex(message, ".*:\\s")
	return to, message
}

// PerformAction evaluates the action associated with the response (speak)
// and performs any necessary actions. Any content that needs to be used in
// the response will be returned.
func PerformAction(reply Reply, speak SpeakData,
				   variable string) (Reply, string) {
	// Handle any included action
	if strings.Contains(speak.Action, "ground") {
		Ground(variable)
	}
	if strings.Contains(speak.Action, "unground") {
		Unground(variable)
	}
	if strings.Contains(speak.Action, "grounded") {
		variable = strings.Join(Dbot.Conf.Grounded, ", ")
	}
	if strings.Contains(speak.Action, "message") {
		to, msg := FormatMessage(variable, speak)
		if len(to) > 0 {
			reply.To = to
		}
		variable = msg
	}
	return reply, variable
}

// HandleTextReplacement determines what to do with each flag in a response
// #a indicates an article "a" or "an"
// #u indicates the name of the user who sent the trigger message
// #v indicates the string captured by the Variable regex
// Other conditionals can be added here. A string with all flags replaced is
// returned.
func HandleTextReplacement(message *hbot.Message, response ResponseData,
						   variable string) string {
	if strings.Contains(response.Message, "#a") {
		// message.Content = AddArticle(message.Content)
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

// FormatReply formulates the bot's response given the message, whether or
// not the sender was an admin (admin_speak), and the index of the SpeakData
// to format the reply to (s_index). It returns the reply with set content and
// destination (but not the time).
func FormatReply(message *hbot.Message, admin_speak bool, s_index int) Reply {
	var reply Reply
	var speakData = getSpeakData(admin_speak)[s_index]
	var rand_index = GetRandomLeastUsedResponseIndex(speakData)
	var response = speakData.Response[rand_index]
	var variable = RemoveTriggerRegex(message.Content, speakData.Regex)
	variable = strings.TrimSpace(GetVariableRegex(variable, speakData.Regex))
	reply.To = ChooseDestination(message)

	if !strings.Contains(speakData.Action, "none") {
		reply, variable = PerformAction(reply, speakData, variable)
		log.Debug(variable)
	}
	response.Message = HandleTextReplacement(message, response, variable)
	log.Debug(response.Message)
	// If reply is non-empty, then bot will send it, so increment response count
	if response.Message != "" {
		speakData.Response[rand_index].Count++
	}
	reply.Content = strings.Split(response.Message, "\n")
	return reply
}

// PerformReply determines whether or not a reply should be formulated and then
// performs it by passing it the bot in use (irc), the message just sent (m),
// and whether or not the sender was the admin (admin_speak). If an action
// was performed, return true.
func PerformReply(irc *hbot.Bot, m *hbot.Message, admin_speak bool) bool {
	speak := getSpeakData(admin_speak)
	// Do not perform an action if either the sender is grounded, is mom/dad,
	// sufficient time has not passed, or the message is from the irc's IP
	if StringInSlice(m.From, Dbot.Conf.Grounded) != -1 ||
	  StringInSlice(m.From, []string{Dbot.Conf.MomName, Dbot.Conf.DadName}) != -1 ||
		MessageRateMet(m) == false ||
		StringInSlice(m.From, []string{Dbot.Conf.Ip, "irc.awest.com"}) != -1 {
		return false
	}
	for i, s := range speak {
		if TestMessage(s.Regex, m) {
			reply := FormatReply(m, admin_speak, i)
			reply.Sent = time.Now()
			numSent := 0
			for _, line := range reply.Content {
				// Make sure line is non-empty before sending
				if len(line) > 0 {
					irc.Msg(reply.To, fmt.Sprintf(line))
					numSent++
				}
				// Make sure there is a timeout between multiple lines in a reply
				if len(reply.Content) > 1 && numSent > 0 {
					time.Sleep(time.Duration(Dbot.Conf.Timeout) * time.Second)
				}
			}
			if numSent > 0 {
				// Record last sent message
				Dbot.LastReply = reply
				UpdateConfig()
				return true
			}
			// If a regex statement passed but nothing was sent,
			// the loop should not continue trying to match the reply to others.
			break
		}
	}
	return false
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

// Prepand the given string with an "a" or "an" based on the first word and
// return the result
func AddArticle(s string) string {
	for _, vowel := range []string{"a", "e", "i", "o", "u"} {
		if strings.Contains(vowel, string(s[0])) {
			return "an " + s
		}
	}
	return "a " + s
}

func getSpeakData(admin_speak bool) []SpeakData {
	var s []SpeakData
	if Dbot.Dad == false {
		s = Dbot.Conf.MomSpeak
	} else if admin_speak {
		s = Dbot.Conf.AdminSpeak
	} else {
		s = Dbot.Conf.Speak
	}
	return s;
}

// UserTrigger is for all non-admin users.
var UserTrigger = hbot.Trigger{
	func(bot *hbot.Bot, m *hbot.Message) bool {
		return (m.From != Dbot.Conf.Admin)
	},
	func(irc *hbot.Bot, m *hbot.Message) bool {
		PerformReply(irc, m, false)
		UpdateConfig()
		return false
	},
}

// AdminTrigger is for the admin user. If no admin response is performed,
// a user reponse is attempted.
var AdminTrigger = hbot.Trigger{
	func(bot *hbot.Bot, m *hbot.Message) bool {
		return (m.From == Dbot.Conf.Admin)
	},
	func(irc *hbot.Bot, m *hbot.Message) bool {
		responded := PerformReply(irc, m, true)
		if !responded {
			PerformReply(irc, m, false)
		}
		UpdateConfig()
		return false
	},
}
