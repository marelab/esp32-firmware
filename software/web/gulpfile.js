const gulp = require("gulp");

const run = require("gulp-run-command").default;

gulp.task("bundle-js", function () {
    const glob = require("glob");
    const browserify = require("browserify");
    const tsify = require("tsify");
    const fancy_log = require("fancy-log");
    const source = require("vinyl-source-stream");
    const buffer = require("vinyl-buffer");
    const uglify = require("gulp-uglify");

    var files = glob.sync('./src/t*/**/*.ts'); // match typings and ts
    files.push("./src/main.ts");

    return browserify({ // Collect js dependencies
        basedir: ".",
        debug: false,
        entries: files,//["src/main.ts"],
        cache: {},
        packageCache: {},
    })
        .plugin(tsify, {files: []}) // Compile typescript
        .bundle()
        .on("error", fancy_log)
        .pipe(source("bundle.js")) // Collect in bundle.js
        .pipe(buffer())
        // TODO: for some reason meter_chart_change_time gets removed by the default config
        // This config costs about 5kb
        .pipe(
            uglify(/*{
                compress: { unused: false },
                mangle: { reserved: ["meter_chart_change_time"] },
            }*/)
        )
        .pipe(gulp.dest("build")); // Write to build/bundle.js(.map)
});

// Write minified html to build/index.html
gulp.task("copy-html", function () {
    const htmlmin = require("gulp-html-minifier-terser");
    const inlineimg = require('gulp-inline-image-html');

    return gulp
        .src(["src/index.html"])
        .pipe(inlineimg('src'))
        .pipe(
            htmlmin({
                collapseBooleanAttributes: true,
                collapseInlineTagWhitespace: true,
                collapseWhitespace: true,
                conservativeCollapse: true,
                decodeEntities: true,
                includeAutoGeneratedTags: false,
                minifyCSS: true,
                minifyJS: true,
                minifyURLs: true,
                preventAttributesEscaping: true,
                processConditionalComments: true,
                removeAttributeQuotes: true,
                removeComments: true,
                removeEmptyAttributes: true,
                removeOptionalTags: true,
                removeRedundantAttributes: true,
                removeScriptTypeAttributes: true,
                removeStyleLinkTypeAttributes: true,
                sortAttributes: true,
                sortClassName: true,
                trimCustomFragments: true,
                useShortDoctype: true,
            })
        )
        .pipe(gulp.dest("build"));
});

gulp.task("sass", function () {
    const { sass } = require("@mr-hope/gulp-sass");
    const postcss = require("gulp-postcss");
    const autoprefixer = require("autoprefixer");
    const cssnano = require("cssnano");

    return gulp
        .src("src/main.scss")
        .pipe(sass()) // Compile sass to css
        .pipe(
            postcss([
                autoprefixer(), // Add browser-specific prefixes
                cssnano({ // Minify css
                    preset: "advanced",
                }),
            ])
        )
        .pipe(gulp.dest("build")); // Write to build/main.css
});

gulp.task("default",
    gulp.series(
        gulp.parallel("copy-html"),
        gulp.parallel("sass"),
        "bundle-js"
    )
);
