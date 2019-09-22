package bot

import (
	"testing"
)

func TestIsRegexVar(t *testing.T) {
	tables := []struct {
		param  string
		expect bool
	}{
		{"", false},
		{"#ahh", false},
		{"ahh#", false},
		{"#ahh ahh#", false},
		{"#ahhahh# ", false},
		{" #ahhahh#", false},
		{" #ahhahh#", false},
		{"ahhahh", false},
		{"#ahhahh#", true},
		{"#123#", true},
		{"#123ahh#", true},
	}
	for i, table := range tables {
		if isRegexVar(table.param) != table.expect {
			t.Errorf("Failed[%d]: expected %+v, got %+v", i, table.expect, !table.expect)
		}
	}
}
