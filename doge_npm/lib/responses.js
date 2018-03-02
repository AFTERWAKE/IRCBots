module.exports = function(){

  var RESPONSES = [
    "Wow!"
  ],
  max = RESPONSES.length;

  return function( nick ) {
    var idx = Math.floor( Math.random() * max );
    return RESPONSES[ idx ].replace( "{{nick}}", nick );
  };
}
