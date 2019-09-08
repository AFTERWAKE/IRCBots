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

func getVar(name string, regexVars []Variable) *Variable {
	for _, regexVar := range regexVars {
		if regexVar.Name == name {
			return &regexVar
		}
	}
	return nil
}
