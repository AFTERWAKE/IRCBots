// regex.js
// ========

module.exports.dadNameTriggers = [
    new RegExp(/(^|\W+)dad(dy|a)?($|\W+|,)/i),
    new RegExp(/(^|\W+)father($|\W+|,)/i),
    new RegExp(/(^|\W+)(pop){1,2}(s)?($|\W+|,)/i),
    new RegExp(/(^|\W+)(pa){1,2}($|\W+|,)/i)
];

module.exports.momNameTriggers = [
    new RegExp(/(^|\W+)mom(my|ma)?($|\W+|,)/i),
    new RegExp(/(^|\W+)mother($|\W+|,)/i),
    new RegExp(/(^|\W+)(ma){1,2}($|\W+|,)/i)
];

module.exports.hiImDadTriggers = [
    new RegExp(/(^|\W+)i(')?m .*$/i)
];

module.exports.goodMorning = [
    new RegExp(/^(good)?\s?morning(,)?/i)
];

module.exports.goodBye = [
    new RegExp(/^(good)?\s?bye(,)?/i)
];

module.exports.testRegexList = function (regexList, message) {
    match = false;
    regexList.forEach(function( regex ) {
        // console.log(regex, regex.test(message));
        if (regex.test(message)) {
            match = true;
        }
    });
    return match;
};