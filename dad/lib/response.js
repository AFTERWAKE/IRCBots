// response.js
// ========

var conf = require('../config.json');

module.exports.testMessage = function (regexList, from, message) {
    match = false;
	if (conf.ignore.includes(from))
	{
		console.log("Ignoring message from %s", from);
		return match;
	}
    regexList.forEach(function( regex ) {
        // console.log(regex, RegExp(regex, 'i').test(message));
        if (RegExp(regex, 'i').test(message)) {
            match = true;
        }
    });
    return match;
};