package dad

import (
	"fmt"
	"math/rand"
	"regexp"
	"strings"
	"time"

	"github.com/whyrusleeping/hellabot"
	// log "gopkg.in/inconshreveable/log15.v2"
)

// FormatReply formulates the bot's response given the message, whether or
// not the sender was an admin (adminSpeak), and the index of the SpeakData
// to format the reply to (sIndex). It returns the reply with set content and
// destination (but not the time). Message content is split into multiple
// messages anywhere a "\n" is found
func (ib *IRCBot) FormatReply(message *hbot.Message, adminSpeak bool, sIndex int) Reply {
	var reply Reply
	var speakData = ib.getSpeakData(adminSpeak, sIndex)
	var response = speakData.GetRandomLeastUsedResponse()
	var variable = RemoveTriggerRegex(message.Content, speakData.Regex)
	variable = strings.TrimSpace(GetVariableRegex(variable, speakData.Regex))
	if (message.Params[0] == ib.BotConfig.Name) {
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
		reply, variable = ib.PerformAction(reply, speakData, variable)
		// log.Debug(variable)
	}
	if joke.MatchString(speakData.Action) {
		if rand.Intn(configJokeOddsOutOf) > configJokeOdds {
			reply.Content = GetICanHazDadJoke()
			// TODO this is a really dirty move to get around incrementing
			// config jokes
			response.Count--
		}
	}
	reply.Content = HandleTextReplacement(message, response, variable)
	// If reply is non-empty, then bot will send it, so increment response count
	if len(reply.Content) > 0 {
		response.Count++
		ib.UpdateBotConfig()
	}
	return reply
}

// PerformReply determines whether or not a reply should be formulated and then
// performs it by passing it the bot in use (bot), the message just sent (m),
// and whether or not the sender was the admin (adminSpeak). If an action
// was performed, return true.
func (ib *IRCBot) PerformReply(m *hbot.Message, adminSpeak bool) bool {
	// Do not perform an action if either the sender is grounded, is mom/dad,
	// sufficient time has not passed, or the message is from the irc's IP
	if StringInSlice(m.From, ib.Muted.Users) != -1 ||
		StringInSlice(m.From, ib.Muted.Bots) != -1 ||
		ib.MessageRateMet(m) == false ||
		StringInSlice(m.From, []string{ib.IRCConfig.IP, "irc.awest.com"}) != -1 {
		return false
	}
	if adminSpeak {
		return ib.performAdminReply(m)
	} else {
		return ib.performUserReply(m)
	}
}

func (ib *IRCBot) performAdminReply(m *hbot.Message) bool {
	for i, s := range ib.BotConfig.AdminSpeak {
		if ib.TestMessage(s.Regex, m) {
			reply := ib.FormatReply(m, true, i)
			return ib.SendReply(m, reply)
		}
	}
	return false
}

func (ib *IRCBot) performUserReply(m *hbot.Message) bool {
	for i, s := range ib.BotConfig.Speak {
		if ib.TestMessage(s.Regex, m) {
			reply := ib.FormatReply(m, false, i)
			return ib.SendReply(m, reply)
		}
	}
	return false
}

// SendMessageType accepts the bot and message and sends a message (msg) to the
// specified user/channel (to) of type replyType.
func (ib *IRCBot) SendMessageType(m *hbot.Message, to string, replyType int, msg string) {
	switch replyType {
	case ReplyType:
		ib.Bot.Reply(m, msg)
	case MessageType:
		to, msg = GetChannelTargetOrDefault(to, msg)
		ib.Bot.Msg(to, msg)
	case NoticeType:
		to, msg = GetChannelTargetOrDefault(to, msg)
		ib.Bot.Notice(to, msg)
	case ActionType:
		to, msg = GetChannelTargetOrDefault(to, msg)
		ib.Bot.Action(to, msg)
	case TopicType:
		to, msg = GetChannelTargetOrDefault(to, msg)
		ib.Bot.Topic(to, msg)
	case SendType:
		ib.Bot.Send(msg)
	case ChModeType:
		to, msg = GetChannelTargetOrDefault(to, msg)
		sliceUserMode := strings.SplitN(msg, " ", 2)
		ib.Bot.ChMode(sliceUserMode[1], to, sliceUserMode[0])
	case JoinType:
		ib.Bot.Join(msg)
	case PartType:
		ib.Bot.Send(fmt.Sprintf("PART %s", msg))
	case QuitType:
		ib.Bot.Send(fmt.Sprintf("QUIT %s", msg))
	}
}

// SendReply accepts the bot, message, and the bot's reply.
// It returns true if at least one line was sent, and false if
// nothing was sent.
func (ib *IRCBot) SendReply(m *hbot.Message, reply Reply) bool {
	numSent := 0
	slicedReplyContent := strings.Split(reply.Content, "\n")
	for _, line := range slicedReplyContent {
		// Make sure line is non-empty before sending
		if len(line) > 0 {
			ib.SendMessageType(m, reply.To, reply.Type, line)
			numSent++
			if numSent == 1 {
				// Record time of first line being sent
				reply.Sent = time.Now()
				ib.LastReply = reply
			}
		}
		// Make sure there is a timeout between multiple lines in a reply
		if len(reply.Content) > 1 && numSent > 0 {
			time.Sleep(time.Duration(ib.IRCConfig.Timeout) * time.Second)
		}
	}
	if numSent > 0 {
		return true
	}
	return false
}

// TestMessage tests the passed message against the passed regex and returns
// whether or not a match was found
func (ib *IRCBot) TestMessage(regex RegexData, message *hbot.Message) bool {
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
