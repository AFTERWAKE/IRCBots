package bot

import (
	"regexp"
)

func isRegexVar(m string) bool {
	r, _ := regexp.Compile("^#\\w+#$")
	return r.MatchString(m)
}
