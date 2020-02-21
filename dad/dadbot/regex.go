package dad

import (
	"regexp"
)

// RemoveTriggerRegex removes Trigger matching substrings from
// the given string
// This doesn't necessarily leave behind the Variable portion, as there could
// be additional message content that matches neither the Trigger nor Variable.
func RemoveTriggerRegex(s string, regex RegexData) string {
	var substring string
	t, _ := MustCompileRegexData(regex)
	substring = t.ReplaceAllLiteralString(s, "")
	return substring
}

// GetVariableRegex returns only the part of the string that matches the
// Variable portion of RegexData
func GetVariableRegex(s string, regex RegexData) string {
	v := regexp.MustCompile(regex.Variable)
	// log.Debug(fmt.Sprintf("Variable regex matched '%s' from '%s'", v.FindString(s), s))
	return v.FindString(s)
}

// RemoveLiteralRegex removes a matching literal that is passed as regex from
// the given string, s, and returns the result.
func RemoveLiteralRegex(s string, regex string) string {
	r := regexp.MustCompile(regex)
	return r.ReplaceAllLiteralString(s, "")
}

// MustCompileRegexData compiles and returns all parts of the passed RegexData variable
func MustCompileRegexData(regex RegexData) (*regexp.Regexp,
	*regexp.Regexp) {
	return regexp.MustCompile(regex.Trigger),
		regexp.MustCompile(regex.Variable)
}
