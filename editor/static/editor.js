// var $, CodeMirror, rascal;

// var bFileChanged = true;
// 
// function fileChanged () {
//     if (!bFileChanged) {
//         $('#location-bar').html($('#location-bar').html() + '&nbsp;*');
//         bFileChanged = true;
//     }
// }

// Set up globals
var ROOT = '/var/www/public/';
var IMAGE_EXTENSIONS = [ 'png', 'jpg', 'jpeg', 'gif', 'ico' ];
var editor;
var preferences = { };

// fileTree operations
function displayLocation(path) {
    "use strict";
    var fpath = path.split(ROOT).pop();
    if (fpath.match(/templates\//)) {
        $('#location-bar').html('<a href="' + fpath.split('templates').pop() + '">' + fpath + '</a>');
    } else {
        $('#location-bar').text(fpath);
    }
    $('#path').val(fpath);
}

function displayTree(path) {
    "use strict";
    $('#filetree').fileTree({
        root: ROOT,
        script: '/editor/get_dirlist',
        multiFolder: false,
        expandedPath: path,
        expandOnce: true,
        extendBindTree: rascal.dnd.bindTree
    }, function (path) {
        var ext = path.split('.').pop().toLowerCase();
        if ($.inArray(ext, IMAGE_EXTENSIONS) >= 0) {
            showPicture(path);
        } else {
            hidePicture();
            $.post('/editor/read', 'path=' + path.split(ROOT).pop(), function (response) {
                editorSetText(response, ext);
                displayLocation(path);
            });
        }
    });
}

function moveItem(src, dst) {
    "use strict";
    console.log('moveItem ' + src + ' ' + dst);
    $.post('/editor/move_item', { src: src, dst: dst }, function (response) {
        var srcDirs = (src.match(/.*\//)[0]).split('/'),
            dstDirs = dst.split('/'),
            jqDst = $('li.directory > a[rel="' + dst + '"]');
        // If src is a directory, reduce by one
        if (srcDirs.join('/') === src) {
            srcDirs.pop();
        }
        // Optimise redisplay of fileTree
        if (dst === ROOT) {
            console.log('move to top');
            displayTree(src);
        } else if (srcDirs.length === dstDirs.length) {
            console.log('optimise equal paths');
            $('li > a[rel="' + src + '"]').hide('slow');
            jqDst.click();
        } else if (srcDirs.length < dstDirs.length) {
            console.log('optimise deeper');
            if (jqDst.parent().hasClass('expanded')) {
                jqDst.click();
            }
            $('li > a[rel="' + src + '"]').hide('slow');
            jqDst.click();
        } else {
            console.log('optimise shallower');
            if (jqDst.parent().hasClass('expanded')) {
                jqDst.click();
            }
            jqDst.click();
        }
        if (src.split(ROOT).pop() === $('#path').val()) {
            displayLocation((dst + src.split('/').pop()).split(ROOT).pop());
        }
    });
}

var deleteFileBusy = false;     // Use semaphore to avoid repeated deletions

$('li.file').live('mouseenter mouseleave', function (event) {
    "use strict";
    if (event.type === 'mouseenter') {
        $(this).children('a').addClass('selected');
        $(this).children('img').addClass('selected');
        $(this).children('img').click(function () {
            var jqel;
            if (!deleteFileBusy) {
                deleteFileBusy = true;
                jqel = $(this).parent();
                $.post('/editor/delete_template', { filename: $(this).siblings('a').text() }, function () {
                    deleteFileBusy = false;
                    jqel.hide('slow');
                    editorSetText('File deleted.');
                });
            }
        });
    } else {
        $(this).children('a').removeClass('selected');
        $(this).children('img').removeClass('selected');
    }
});

function initRascalDnd() {
    "use strict";
    var rd = rascal.dnd;
    rd.root = ROOT;
    rd.container = 'filetree';
    rd.notDraggable = ['/var/www/public/server.py',
            '/var/www/public/static/', '/var/www/public/templates/'];
    rd.itemDropped = moveItem;
    rd.filesDropped = uploadItems;
    rd.init();
}

// file operations
function saveProgress(pc) {
    // console.log('progress ' + pc);
    $('#save-progress').css('background-position', pc + '% 0');
}

function saveMsg(msg) {
    $('#save-message').text(msg)
        .css('visibility', 'visible')
        .hide()
        .fadeTo(500, 1)
        .fadeTo(2000, 0);
}

function saveFile() {
    "use strict";
    var s = editorGetText();
    $.post('/editor/save', { path: $('#path').val(), text: s });
    $('#save-progress').css('background-position', '-120px');
    $('#save-progress').animate({ 'background-position': 0 }, 1000, function () {
        saveMsg('Saved file');
    });
}

// Function for binding ctrl keystrokes from Ganeshji Marwaha:
// http://www.gmarwaha.com/blog/2009/06/16/ctrl-key-combination-simple-jquery-plugin/
$.ctrl = function (key, callback, args) {
    "use strict";
    $(document).keydown(function (e) {
        if (!args) {
            args = [];  // IE barks when args is null
        }
        // if (e.keyCode === key.charCodeAt(0) && e.ctrlKey) {
        if (e.keyCode === key.charCodeAt(0) && e.metaKey) {
            callback.apply(this, args);
            return false;
        }
    });
};

$.ctrl('S', function () {
    "use strict";
    console.log('ctrl-S');
    saveFile();
});

$('#save').click(function () {
    "use strict";
    saveFile();
});

// glue between fileTree dnd and upload
function uploadStatus (msg) {
    editorSetText(editorGetText() + msg + '\n');
}

function uploadComplete(directory) {
    console.log('uploadComplete ' + ROOT + directory);
    saveMsg('Upload complete');
    var dst = ROOT + directory,
        jqDst = $('li.directory > a[rel="' + dst + '"]');
    if (dst === ROOT) {
        displayTree('');
    } else {
        if (jqDst.parent().hasClass('expanded')) {
            jqDst.click();
        }
        jqDst.click();
    }
}

function uploadItems(files, dst) {
    var ru = rascal.upload;
    // set up postUrl, allowed types, progress, status and complete
    ru.postUrl = '/editor/xupload';
    ru.allowedTypes = [ 'image/', 'text/html', 'text/css', 'application/x-javascript', 'text/x-python-script' ];
    ru.progress = saveProgress;
    ru.status = uploadStatus;
    ru.complete = uploadComplete;
    editorSetText('');
    ru.filesDropped(files, dst.split(ROOT).pop());
}

$('#new-template').click(function () {
    "use strict";
    $('#overlay-t').css('visibility', 'visible');
    $('#template-name').focus();
});

$('#create-template').click(function () {
    "use strict";
    var templateName = $('#template-name').val().trim();
    if (templateName !== '') {
        $.post('/editor/new_template', { templateName: templateName }, function (response) {
            console.log(response);
            displayTree('/var/www/public/templates/');
            $('#overlay-t').css('visibility', 'hidden');
        });
    }
});

$('#cancel-template').click(function () {
    "use strict";
    $('#overlay-t').css('visibility', 'hidden');
});

$('#new-folder').click(function () {
    "use strict";
    $('#overlay-f').css('visibility', 'visible');
    $('#folder-name').focus();
});

$('#create-folder').click(function () {
    "use strict";
    var folderName = $('#folder-name').val().trim();
    if (folderName !== '') {
        $.post('/editor/new_folder', { folderName: folderName }, function (response) {
            console.log(response);
            displayTree('/var/www/public/static/');
            $('#overlay-f').css('visibility', 'hidden');
        }).error(function (jqXHR, textStatus, errorThrown) {
            console.log('new_folder: ' + textStatus + ': ' + errorThrown);
            if (errorThrown === 'Conflict') {
                $('#folder-message').text('Folder exists - please use a different name')
                    .css('color', 'red');
            } else {    // 'Bad Request'
                $('#folder-message').text('Folder could not be created (mkdir returned an error)')
                    .css('color', 'red');
            }
        });
    }
});

$('#cancel-folder').click(function () {
    "use strict";
    $('#overlay-f').css('visibility', 'hidden');
});

function initPreferences () {
    "use strict";
    getPreferences();
    // Save and Delete warnings in this file
    bindEditPreferences();
}

$('#preferences').click(function () {
    "use strict";
    $('#overlay-p').css('visibility', 'visible');
    console.log('Preferences ' + JSON.stringify(preferences));
});

$('#cancel-prefs').click(function () {
    "use strict";
    $('#overlay-p').css('visibility', 'hidden');
    console.log('Preferences ' + JSON.stringify(preferences));
});

// Reload pytronics
$('#reload').click(function () {
    "use strict";
    $.post('/editor/reload', 'text');
    $('#reload-progress').css('background-position', '-120px');
    $('#reload-progress').animate({ 'background-position': 0 }, 10000);
});
