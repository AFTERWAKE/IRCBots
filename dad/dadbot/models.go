package dad

import (
	"github.com/whyrusleeping/hellabot"
	"time"
)

// IRCConfig contains all content that should be common between the bots
type IRCConfig struct {
	Admin       string
	IP          string
	MessageRate int
	Timeout     int
}

// DadConfig gives structure to dad's config file
type DadConfig struct {
	AdminSpeak []SpeakData
	Channels   []string
	Debug      bool
	Grounded   []string
	Name       string
	Speak      []SpeakData
}

// MomConfig gives structure to mom's config file
type MomConfig struct {
	AdminSpeak []SpeakData
	Channels   []string
	Debug      bool
	Name       string
	Speak      []SpeakData
}

// Configuration lists all the high-level content of the config file
type Configuration struct {
	Admin       string
	AdminSpeak  []SpeakData
	Channels    []string
	DadName     string
	Debug       bool
	Grounded    []string
	IP          string
	MessageRate int // Using 1 reply per x seconds
	MomName     string
	MomSpeak    []SpeakData
	Speak       []SpeakData
	Timeout     int // Timeout between multi-lined reply
}

// SpeakData is the regex-to-response pairing for each possible response.
// There can be more than one response, and it will be chosen semi-randomly.
type SpeakData struct {
	Action   string
	Regex    RegexData
	Response []ResponseData
}

// ResponseData contains the bot's reply and the number of times the reply
// has been sent. Message may contain [...] blocks for different types of
// text replacement/manipulation.
type ResponseData struct {
	Message string
	Count   int
}

// RegexData makes it a little easier to capture text by having
// regex that seperates the message content into two parts.
// The Trigger section acts as the command that the bot responds to.
// The Variable is what the bot will take and use in its response (if needed).
// If no reuse of message content is needed in a response, leave Variable blank.
type RegexData struct {
	Trigger  string
	Variable string
}

// Reply includes the final formatted response (all text replacement blocks
// dealt with), the destination, and the time the message was sent at.
type Reply struct {
	Content []string
	To      string
	Sent    time.Time
}

// IRCBot is an extension of hellabot's Bot that includes an indicator for
// whether the bot is acting as mom or dad, the config information, and the
// last reply sent by the bot
type IRCBot struct {
	Bot       *hbot.Bot
	Conf      IRCConfig
	LastReply Reply
}

// ICanHazDadJoke declares the expected json format of jokes from
// ICanHazDadJoke.com
type ICanHazDadJoke struct {
	ID     string `json:"id"`
	Joke   string `json:"joke"`
	Status int    `json:"status"`
}
