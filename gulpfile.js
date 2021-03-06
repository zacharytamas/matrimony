
var gulp = require('gulp');
var $ = require('gulp-load-plugins')();
var browserSync = require('browser-sync');
var merge = require('merge-stream');
var path = require('path');

function distPath(path) {
  return 'static/dist/' + path;
}

var styleTask = function(stylesPath, srcs) {
  return gulp
    .src(srcs.map(function(src) {
      return path.join('static', stylesPath, src); }
    ))
    // .pipe($.changed('static/' + stylesPath, {extension: '.css'}))
    // TODO possibly add CSS minification here
    .pipe(gulp.dest('static/dist/' + stylesPath))
    .pipe($.size({title: stylesPath}));
};

gulp.task('styles', styleTask.bind(gulp, '', ['*.css']));

gulp.task('sass', function() {
  return gulp
    .src(['static/*.scss'])
    .pipe($.sass().on('error', $.sass.logError))
    .pipe(gulp.dest('static/dist'))
    .pipe($.size({title: 'sass'}));
});

gulp.task('copy', function() {
  var bower = gulp.src([
    'bower_components/**/*'
  ]).pipe(gulp.dest(distPath('bower_components')));

  // var elements = gulp.src(['static/elements-*.html'])
  //   .pipe(gulp.dest(distPath('elements')));

  // var vulcanizeCore = gulp.src(['static/elements-core.html'])
  //   .pipe($.rename('core.vulcanized.html'))
  //   .pipe(gulp.dest(distPath('elements')));

  return merge(bower)
    .pipe($.size({title: 'copy'}));
});

// Vulcanize imports
gulp.task('vulcanize', function() {
  var DEST_DIR = 'static/dist';

  return gulp.src('static/elements-core.html')
    .pipe($.vulcanize({
      stripComments: true,
      inlineCss: true,
      inlineScripts: true,
      stripExcludes: false
    }))
    .pipe(gulp.dest(DEST_DIR))
    .pipe($.size({title: 'vulcanize'}));
});

gulp.task('develop', function() {
  gulp.watch(['static/*.css'], ['styles']);
  gulp.watch(['static/*.scss'], ['sass']);
  gulp.watch(['static/elements-*.html', 'static/elements/**/*'], ['vulcanize']);
});
