package bot_test

import (
	"testing"

	"github.com/AFTERWAKE/IRCBots/dad/bot"
)

func TestRegexMatch(t *testing.T) {
	botVars := []bot.Variable{
		bot.Variable{"#example1#", []bot.Regex{bot.Regex{[]string{"t+"}}}, []string{""}, ""},
		bot.Variable{"#example2#", []bot.Regex{bot.Regex{[]string{"mid{3,5}le"}}}, []string{""}, ""},
		bot.Variable{"@capture1@", []bot.Regex{bot.Regex{[]string{"[1-4][a-f]"}}}, []string{""}, ""},
		bot.Variable{"@capture2@", []bot.Regex{bot.Regex{[]string{"me+p"}}}, []string{""}, ""},
	}
	tables := []struct {
		regex     *bot.Regex
		param     string
		expect    bool
		remaining string
	}{
		{&bot.Regex{[]string{"^test", "pattern$"}}, "test pattern", false, " "},
		{&bot.Regex{[]string{"^test", "pattern$"}}, "testpattern", true, ""},
		{&bot.Regex{[]string{"^test", "pattern$"}}, "blahpattern", false, "blahpattern"},
		{&bot.Regex{[]string{"^t{1,4}", "#example1#", "pattern$"}}, "ttttttpattern", true, ""},
		{&bot.Regex{[]string{"#example2#"}}, "ttttttpattern", false, "ttttttpattern"},
		{&bot.Regex{[]string{"middle", "#example2#", "pattern$"}}, "middlemidddlepattern", true, ""},
		// {&bot.Regex{[]string{".*", "@capture1@", "something"}}, "blahblah1fsomething", true, ""},
		// {&bot.Regex{[]string{".*", "@capture2@", "something"}}, "blahmeepsomething", true, ""},
	}
	for i, table := range tables {
		match, remaining := table.regex.Match(table.param, botVars, 0)
		if match != table.expect || remaining != table.remaining {
			t.Errorf("Failed [%d]: expected match: %v, got %v, remaining: \"%s\", got \"%s\"", i, table.expect, match, table.remaining, remaining)
		}
	}
}
