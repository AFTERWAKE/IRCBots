package bot_test

import (
	"reflect"
	"testing"

	"github.com/AFTERWAKE/IRCBots/dad/bot"
)

func TestCommandMatch(t *testing.T) {
	command := &bot.Command{
		Regex: []*bot.Regex{
			{Pattern: "^testpattern$"},
			{Pattern: "[^a]([b-z]+)"},
		},
		Responses:   []*bot.Response{nil},
		Permissions: []string{},
	}
	tables := []struct {
		param  string
		expect []string
	}{
		{"test pattern", []string{"test", "est"}},
		{"testpattern", []string{"testpattern"}},
		{"blahpattern", []string{"bl", "l"}},
		{"ttttttpattern", []string{"ttttttp", "tttttp"}},
		{"aaaa", nil},
	}
	for i, table := range tables {
		match, _ := command.Match(table.param)
		if !reflect.DeepEqual(match, table.expect) {
			t.Errorf(
				"Failed [%d]: expected match: %v, got %v",
				i, table.expect, match,
			)
		}

	}
}

func TestCommand_GetResponse(t *testing.T) {
	command := &bot.Command{
		Regex: nil,
		Responses: []*bot.Response{
			{[]string{"1"}, nil},
			{[]string{"2"}, nil},
			{[]string{"3"}, nil},
		},
		Permissions: nil,
	}
	for i := 0; i <= 10; i++ {
		resp := command.GetResponse()
		if resp == nil {
			t.Errorf("Failed [%d]: expected a response, but got nil", i)
		}
	}
}
