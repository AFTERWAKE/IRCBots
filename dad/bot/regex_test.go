package bot_test

import (
	"reflect"
	"testing"

	"github.com/AFTERWAKE/IRCBots/dad/bot"
)

func TestRegexMatch(t *testing.T) {
	tables := []struct {
		regex  *bot.Regex
		param  string
		expect []string
	}{
		{&bot.Regex{"^testpattern$"}, "test pattern", nil},
		{&bot.Regex{"^testpattern$"}, "testpattern", []string{"testpattern"}},
		{&bot.Regex{"^testpattern$"}, "blahpattern", nil},
		{&bot.Regex{"^t{1,4}(t+)pattern$"}, "ttttttpattern", []string{"ttttttpattern", "tt"}},
	}
	for i, table := range tables {
		match := table.regex.Match(table.param)
		if !reflect.DeepEqual(match, table.expect) {
			t.Errorf(
				"Failed [%d]: expected match: %v, got %v",
				i, table.expect, match,
			)
		}
	}
}
