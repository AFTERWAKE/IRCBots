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
		match, _ := table.regex.Match(table.param)
		if !reflect.DeepEqual(match, table.expect) {
			t.Errorf(
				"Failed [%d]: expected match: %v, got %v",
				i, table.expect, match,
			)
		}
	}
}

func TestRegexReplace(t *testing.T) {
	tables := []struct {
		regex    *bot.Regex
		message  string
		response string
		expect   string
	}{
		{&bot.Regex{Pattern: "\\bground\\s+(?P<target>\\S+)\\b"}, "blah blah ground this guy", "grounded $target", "grounded this"},
		{&bot.Regex{Pattern: "\\bground\\s+(?P<target>\\S+)\\b"}, "ground some_dude", "grounded $target", "grounded some_dude"},
		{&bot.Regex{Pattern: "\\bground\\s+(?P<target>\\S+)\\b"}, "unground this guy", "grounded $target", ""},
	}
	for i, table := range tables {
		replace := table.regex.Replace(table.message, table.response)
		if replace != table.expect {
			t.Errorf(
				"Failed [%d]: expected match: %v, got: %v",
				i, table.expect, replace,
			)
		}
	}
}
