package bot_test

import (
	"testing"

	"github.com/AFTERWAKE/IRCBots/dad/bot"
)

func TestVariableMatch(t *testing.T) {
	botVars := []bot.Variable{
		bot.Variable{"#example1#", []bot.Regex{bot.Regex{[]string{"t+"}}}, []string{""}, ""},
		bot.Variable{"#example2#", []bot.Regex{bot.Regex{[]string{"mid{3,5}le"}}}, []string{""}, ""},
		bot.Variable{"@capture1@", []bot.Regex{bot.Regex{[]string{"[1-4][a-f]"}}}, []string{""}, ""},
		bot.Variable{"@capture2@", []bot.Regex{bot.Regex{[]string{"me+p"}}}, []string{""}, ""},
	}
	tables := []struct {
		variable  bot.Variable
		param     string
		expect    bool
		remaining string
	}{
		{botVars[0], "test pattern", true, "est pattern"},
		{botVars[0], "tttttt", true, ""},
		{botVars[0], "meep", false, "meep"},
		{botVars[0], "blahpattern", true, "blahpaern"},
		{botVars[1], "middlemidddlepattern", true, "middlepattern"},
		{botVars[2], "blahblah1fsomething", true, "blahblahsomething"},
		{botVars[3], "meep", true, ""},
	}
	for i, table := range tables {
		match, remaining := table.variable.Match(table.param, botVars, 0)
		if match != table.expect || remaining != table.remaining {
			t.Errorf("Failed [%d]: expected match: %v, got %v, remaining: \"%s\", got \"%s\"", i, table.expect, match, table.remaining, remaining)
		}
	}
}
