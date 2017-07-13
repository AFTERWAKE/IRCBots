// regex.js
// ========

module.exports.testRegexList = function (regexList, message) {
    match = false;
    regexList.forEach(function( regex ) {
        // console.log(regex, RegExp(regex, 'i').test(message));
        if (RegExp(regex, 'i').test(message)) {
            match = true;
        }
    });
    return match;
};