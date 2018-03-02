// Package dad is an extension of hellabot that plays the role of an IRC
// chat bot, either as a mom or a dad
package dad

import (
	"flag"
	"fmt"
	"math/rand"
	"regexp"
	"strings"
	"time"

	"github.com/whyrusleeping/hellabot"
	log "gopkg.in/inconshreveable/log15.v2"
)

var Dad bool

// Dbot is the global variable that primarily allows for the config information
// to be smoothly passed around and updated properly.
var Dbot DadConfig
var Irc IRCBot
var Mbot MomConfig
var ircConfigFile = "irc_config.json"
var dadConfigFile = "dad_config.json"
var momConfigFile = "mom_config.json"

// UserTrigger is for all non-admin users.
var UserTrigger = hbot.Trigger{
	func(bot *hbot.Bot, m *hbot.Message) bool {
		return (m.From != Irc.Conf.Admin)
	},
	func(irc *hbot.Bot, m *hbot.Message) bool {
		PerformReply(irc, m, false)
		return false
	},
}

// AdminTrigger is for the admin user. If no admin response is performed,
// a user reponse is attempted.
var AdminTrigger = hbot.Trigger{
	func(bot *hbot.Bot, m *hbot.Message) bool {
		return (m.From == Irc.Conf.Admin)
	},
	func(irc *hbot.Bot, m *hbot.Message) bool {
		responded := PerformReply(irc, m, true)
		if !responded {
			PerformReply(irc, m, false)
		}
		return false
	},
}

// Run starts an instance of the bot, with variable dad indicating whether
// the bot should behave like a dad or a mom
func Run(dad bool) {
	Dad = dad
	var nickStr string
	rand.Seed(time.Now().Unix())
	flag.Parse()
	Irc.Conf, Dbot, Mbot = ReadConfig()
	if Dad {
		nickStr = Dbot.Name
	} else {
		nickStr = Mbot.Name
	}
	serv := flag.String("server", Irc.Conf.IP+
		":6667", "hostname and port for irc server to connect to")
	nick := flag.String("nick", nickStr, "nickname for the bot")

	hijackSession := func(bot *hbot.Bot) {
		bot.HijackSession = false
	}
	channels := func(bot *hbot.Bot) {
		if Dad {
			bot.Channels = Dbot.Channels
		} else {
			bot.Channels = Mbot.Channels
		}
	}
	bot, err := hbot.NewBot(*serv, *nick, hijackSession, channels)
	Irc.Bot = bot
	checkErr(err)
	Irc.Bot.AddTrigger(UserTrigger)
	Irc.Bot.AddTrigger(AdminTrigger)
	Irc.Bot.Logger.SetHandler(log.StdoutHandler)
	// Start up bot (this blocks until we disconnect)
	Irc.Bot.Run()
	fmt.Println("Bot shutting down.")
}

// FormatReply formulates the bot's response given the message, whether or
// not the sender was an admin (adminSpeak), and the index of the SpeakData
// to format the reply to (sIndex). It returns the reply with set content and
// destination (but not the time).
func FormatReply(message *hbot.Message, adminSpeak bool, sIndex int) Reply {
	var reply Reply
	var speakData = getSpeakData(adminSpeak)[sIndex]
	var randIndex = GetRandomLeastUsedResponseIndex(speakData)
	var response = speakData.Response[randIndex]
	var variable = RemoveTriggerRegex(message.Content, speakData.Regex)
	variable = strings.TrimSpace(GetVariableRegex(variable, speakData.Regex))
	reply.To = ChooseDestination(message)

	// TODO refactor if all jokes are ever done through http get
	joke := regexp.MustCompile("(?i)^joke$")
	var configJokeOdds = 40
	var configJokeOddsOutOf = 100
	if !strings.Contains(speakData.Action, "none") {
		reply, variable = PerformAction(reply, speakData, variable)
		// log.Debug(variable)
	}
	if joke.MatchString(speakData.Action) {
		if rand.Intn(configJokeOddsOutOf) > configJokeOdds {
			response.Message = GetICanHazDadJoke()
			// TODO this is a really dirty move to get around incrementing
			// config jokes
			speakData.Response[randIndex].Count--
		}
	}
	response.Message = HandleTextReplacement(message, response, variable)
	// If reply is non-empty, then bot will send it, so increment response count
	if response.Message != "" {
		speakData.Response[randIndex].Count++
	}
	reply.Content = strings.Split(response.Message, "\n")
	return reply
}

// PerformReply determines whether or not a reply should be formulated and then
// performs it by passing it the bot in use (irc), the message just sent (m),
// and whether or not the sender was the admin (adminSpeak). If an action
// was performed, return true.
func PerformReply(irc *hbot.Bot, m *hbot.Message, adminSpeak bool) bool {
	speak := getSpeakData(adminSpeak)
	// Do not perform an action if either the sender is grounded, is mom/dad,
	// sufficient time has not passed, or the message is from the irc's IP
	if StringInSlice(m.From, Dbot.Grounded) != -1 ||
		StringInSlice(m.From, []string{Dbot.Name, Mbot.Name}) != -1 ||
		MessageRateMet(m) == false ||
		StringInSlice(m.From, []string{Irc.Conf.IP, "irc.awest.com"}) != -1 {
		return false
	}
	for i, s := range speak {
		if TestMessage(s.Regex, m) {
			reply := FormatReply(m, adminSpeak, i)
			reply.Sent = time.Now()
			numSent := 0
			for _, line := range reply.Content {
				// Make sure line is non-empty before sending
				if len(line) > 0 {
					irc.Msg(reply.To, line)
					numSent++
				}
				if numSent == 1 {
					// Record time of first line being sent
					Irc.LastReply = reply
				}
				// Make sure there is a timeout between multiple lines in a reply
				if len(reply.Content) > 1 && numSent > 0 {
					time.Sleep(time.Duration(Irc.Conf.Timeout) * time.Second)
				}
			}
			if numSent > 0 {
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
