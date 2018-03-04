package dad

import (
	"fmt"
	"math/rand"
	"regexp"
	"strings"
	"time"

	"github.com/whyrusleeping/hellabot"
)

// FormatReply formulates the bot's response given the message, whether or
// not the sender was an admin (adminSpeak), and the index of the SpeakData
// to format the reply to (sIndex). It returns the reply with set content and
// destination (but not the time). Message content is split into multiple
// messages anywhere a "\n" is found
func FormatReply(message *hbot.Message, adminSpeak bool, sIndex int) Reply {
	var reply Reply
	var speakData = getSpeakData(adminSpeak)[sIndex]
	var randIndex = GetRandomLeastUsedResponseIndex(speakData)
	var response = speakData.Response[randIndex]
	var variable = RemoveTriggerRegex(message.Content, speakData.Regex)
	variable = strings.TrimSpace(GetVariableRegex(variable, speakData.Regex))
	if (message.Params[0] == Dbot.Name && Dad) ||
		(message.Params[0] == Mbot.Name && !Dad) {
		reply.To = message.From
	} else {
		reply.To = message.To
	}
	reply.Type = response.Type

	// TODO refactor if all jokes are ever done through http get
	joke := regexp.MustCompile("(?i)^joke$")
	var configJokeOdds = 33
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
// performs it by passing it the bot in use (bot), the message just sent (m),
// and whether or not the sender was the admin (adminSpeak). If an action
// was performed, return true.
func PerformReply(bot *hbot.Bot, m *hbot.Message, adminSpeak bool) bool {
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
			return SendReply(bot, m, reply)
		}
	}
	return false
}

// SendMessageType accepts the bot and message and sends a message (msg) to the
// specified user/channel (to) of type replyType.
func SendMessageType(bot *hbot.Bot, m *hbot.Message, to string, replyType int, msg string) {
	switch replyType {
	case ReplyType:
		bot.Reply(m, msg)
	case MessageType:
		to, msg = GetChannelTargetOrDefault(to, msg)
		bot.Msg(to, msg)
	case NoticeType:
		to, msg = GetChannelTargetOrDefault(to, msg)
		bot.Notice(to, msg)
	case ActionType:
		to, msg = GetChannelTargetOrDefault(to, msg)
		bot.Action(to, msg)
	case TopicType:
		to, msg = GetChannelTargetOrDefault(to, msg)
		bot.Topic(to, msg)
	case SendType:
		bot.Send(msg)
	case ChModeType:
		to, msg = GetChannelTargetOrDefault(to, msg)
		sliceUserMode := strings.SplitN(msg, " ", 2)
		bot.ChMode(sliceUserMode[1], to, sliceUserMode[0])
	case JoinType:
		bot.Join(msg)
	case PartType:
		bot.Send(fmt.Sprintf("PART %s", msg))
	case QuitType:
		bot.Send(fmt.Sprintf("QUIT %s", msg))
	}
}

// SendReply accepts the bot, message, and the bot's reply.
// It returns true if at least one line was sent, and false if
// nothing was sent.
func SendReply(bot *hbot.Bot, m *hbot.Message, reply Reply) bool {
	numSent := 0
	for _, line := range reply.Content {
		// Make sure line is non-empty before sending
		if len(line) > 0 {
			SendMessageType(bot, m, reply.To, reply.Type, line)
			numSent++
			if numSent == 1 {
				// Record time of first line being sent
				reply.Sent = time.Now()
				Irc.LastReply = reply
			}
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
