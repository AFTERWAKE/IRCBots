package bot

import (
	"reflect"
	"testing"
)

func TestIsCaptureVar(t *testing.T) {
	tables := []struct {
		param  string
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

func TestGetVar(t *testing.T) {
	var1 := Variable{"#a#", []Regex{}, []string{}, ""}
	var2 := Variable{"@b@", []Regex{}, []string{}, ""}
	tables := []struct {
		name      string
		regexVars []Variable
		expect    *Variable
	}{
		{"#a#", []Variable{var1, var2}, &var1},
		{"@b@", []Variable{var1, var2}, &var2},
		{"#c#", []Variable{var1, var2}, nil},
		{"@d@", []Variable{var1, var2}, nil},
	}
	for i, table := range tables {
		result := getVar(table.name, table.regexVars)
		if !reflect.DeepEqual(result, table.expect) {
			t.Errorf("Failed[%d]: expected %+v, got %+v", i, table.expect, result)
		}
	}
}
