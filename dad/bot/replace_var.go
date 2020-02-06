package bot

import (
	"fmt"
	"regexp"
)

/**
GetVar takes the target var, the response, and the replacement, and replaces any instances of
<target> in the response with that value
*/
func ReplaceVar(
	target string,
	response []string,
	replacement string,
) []string {
	re := regexp.MustCompile(fmt.Sprintf("(?i)(?P<var><%s>)", target))
	res := make([]string, len(response))
	for i, resp := range response {
		res[i] = re.ReplaceAllString(resp, replacement)
	}
	return res
}
