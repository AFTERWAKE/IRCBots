package bot

import (
	"regexp"
)

func isCaptureVar(m string) bool {
	r, _ := regexp.Compile("^@[\\w\\d]+@$") // TODO This can be a config option!!!
	return r.MatchString(m)
}

func isRegexVar(m string) bool {
	r, _ := regexp.Compile("^#\\w+#$")
	return r.MatchString(m)
}

func convertRegexVar(m string, regexVars []Variable) []string {
	// for _, regexVar := range regexVars {
	// if regexVar.Variable == m {
	// return regexVar.Regex[0].
	// }
	// }
	return []string{}
}
