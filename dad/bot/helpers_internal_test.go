package bot

import (
	"testing"
)

func TestIsCaptureVar(t *testing.T) {
	tables := []struct {
		param string
		expect bool
	}{
		{"", false},
		{"@ahh", false},
		{"ahh@", false},
		{"@ahh ahh@", false},
		{"@ahhahh@ ", false},
		{" @ahhahh@", false},
		{" @ahhahh@", false},
		{"ahhahh", false},
		{"@ahhahh@", true},
		{"@123@", true},
		{"@123ahh@", true},
	}
	for _, table := range tables {
		if isCaptureVar(table.param) != table.expect {
			t.Errorf("Failed: expected %v, got %v", table.expect, !table.expect)
		}
	}
}

func TestIsRegexVar(t *testing.T) {
	tables := []struct {
		param string
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
	for _, table := range tables {
		if isRegexVar(table.param) != table.expect {
			t.Errorf("Failed: expected %v, got %v", table.expect, !table.expect)
		}
	}
}