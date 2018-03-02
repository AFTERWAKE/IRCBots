module.exports = function( grunt ) {
  grunt.initConfig({
    pkg: grunt.file.readJSON( "package.json" ),
    jshint: {
      options: {
        es5: false,
        newcap: false
      },
      files: [
        "Gruntfile.js",
        "app.js"
      ]
    }
  });

  grunt.loadNpmTasks( "grunt-contrib-jshint" );

  grunt.registerTask( "default", [ "jshint" ]);
};
