/*
 * grunt-init-jquery
 * https://gruntjs.com/
 *
 * Copyright (c) 2013 "Cowboy" Ben Alman, contributors
 * Licensed under the MIT license.
 */

'use strict';

// Basic template description.
exports.description = 'Create a new event.';

// Template-specific notes to be displayed before question prompts.
exports.notes = 'A few questions will be asked';

// Template-specific notes to be displayed after question prompts.
exports.after = "You're done";

// Any existing file or directory matching this wildcard will cause a warning.
exports.warnOn = '*';

// The actual init template.
exports.template = function (grunt, init, done) {

    init.process({}, [


        // Prompt for these values.
        init.prompt('name'),
        init.prompt('display_name'),
        init.prompt('webtitle'),

//        init.prompt('description', 'Yet another green doors project.'),
//        init.prompt('version'),
//        init.prompt('homepage'),
//        init.prompt('bugs'),
        init.prompt('licenses', 'MIT'),
//        init.prompt('author_name'),
//        init.prompt('author_email'),
//        init.prompt('author_url'),
        //        init.prompt('title', function (value, data, done) {
//            // Fix jQuery capitalization.
//            value = value.replace(/greendoors/gi, 'Green Doors');
//            done(null, value);
//        }),
//        {
//            name: 'jetpack_support',
//            message: 'Will you use be using Jetpack? [Y/n]',
//            default: 'y'
//        }
    ], function (err, props) {
        // A few additional properties.

//        props.dependencies = {jquery: props.jquery_version || '>= 1'};

        props.keywords = [];

        // Files to copy (and process).
        var files = init.filesToCopy(props);

        //Will they support Jetpack?
//        if (props.jetpack_support.toUpperCase()[0] == "N") {
//            delete files[ 'inc/jetpack.php'];
//        }

        // Add properly-named license files.
        init.addLicenseFiles(files, props.licenses);
        // Actually copy (and process) files.
        init.copyAndProcess(files, props, {noProcess: ['libs/**', 'test.js','templates/app-name/application.html','templates/app-name/debug.html']});
        console.log(files);

        grunt.file.mkdir('static');
        grunt.file.mkdir('data/img/unprocessed');

        // All done!
        done();
    });
};