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
		checkVar  int // -1 if no var value needs checking
		varValue  string
	}{
		// {&bot.Regex{[]string{"^test", "pattern$"}}, "test pattern", false, " ", -1, ""},
		// {&bot.Regex{[]string{"^test", "pattern$"}}, "testpattern", true, "", -1, ""},
		// {&bot.Regex{[]string{"^test", "pattern$"}}, "blahpattern", false, "blahpattern", -1, ""},
		// {&bot.Regex{[]string{"^t{1,4}", "#example1#", "pattern$"}}, "ttttttpattern", true, "", -1, ""},
		// {&bot.Regex{[]string{"#example2#"}}, "ttttttpattern", false, "ttttttpattern", -1, ""},
		// {&bot.Regex{[]string{"middle", "#example2#", "pattern$"}}, "middlemidddlepattern", true, "", -1, ""},
		{&bot.Regex{[]string{".*" /*TODO this ain't it chief*/, "@capture1@", "something"}}, "blahblah1fsomething", true, "", 2, "1f"},
		{&bot.Regex{[]string{".*", "@capture2@", "something"}}, "blahmeepsomething", true, "", 3, "meep"},
	}
	for i, table := range tables {
		match, remaining := table.regex.Match(table.param, botVars, 0)
		if match != table.expect || remaining != table.remaining {
			t.Errorf(
				"Failed [%d]: expected match: %v, got %v, remaining: \"%s\", got \"%s\"",
				i, table.expect, match, table.remaining, remaining,
			)
			if table.checkVar > -1 && botVars[table.checkVar].Value != table.varValue {
				t.Errorf(
					"Failed [%d continued]: varValue: \"%s\", got \"%s\"",
					i, table.varValue, botVars[table.checkVar].Value,
				)
			}
		}

	}
}
