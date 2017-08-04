module.exports = function(){

  var RESPONSES = [
    "{{nick}}, yeah dude!!! http://i.imgur.com/MAiIwW8.gifv",
    "\\o You Rock, {{nick}}",
    "{{nick}}, \\o!!!",
    "{{nick}}, http://24.media.tumblr.com/tumblr_m6h84mAoMS1rwcc6bo1_500.gif",
    "\\o you never cease to amaze me, {{nick}}!",
    "{{nick}}, \\o",
    "{{nick}}, wow, just.. wow. \\o",
    "\\o this is just incredible {{nick}}!",
    "{{nick}}, NO. jk! \\o",
    "Tom would be proud of you, {{nick}} \\o",
    "\\o Thanks {{nick}}!!",
    "{{nick}}, http://i.imgur.com/glFDOpL.gif",
    "{{nick}}, http://i.imgur.com/0rpP0bd.gifv",
    "{{nick}}, http://i.imgur.com/WJKWoCK.gif",
    "....fine then {{nick}} http://i.imgur.com/YED5jgK.gif",
    "{{nick}}, https://i.imgur.com/ybNEq8m.gifv"
  ],
  max = RESPONSES.length;

  return function( nick ) {
    var idx = Math.floor( Math.random() * max );
    return RESPONSES[ idx ].replace( "{{nick}}", nick );
  };
}
