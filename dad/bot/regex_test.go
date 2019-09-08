package bot_test

import (
	"testing"

	"github.com/AFTERWAKE/IRCBots/dad/bot"
)

func TestRegexMatch(t *testing.T) {
	tables := []struct {
		regex  *bot.Regex
		param  string
		expect bool
	}{
		{&bot.Regex{[]string{"^test", "pattern$"}}, "test pattern", false},
		{&bot.Regex{[]string{"^test", "pattern$"}}, "testpattern", true},
		{&bot.Regex{[]string{"^test", "pattern$"}}, "blahpattern", false},
	}
	for i, table := range tables {
		if table.regex.Match(table.param) != table.expect {
			t.Errorf("Failed [%d]: expected %v, got %v", i, table.expect, !table.expect)
		}
	}
}
