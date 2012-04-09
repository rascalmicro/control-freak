// var $, CodeMirror, rascal;

// Set up globals
var ROOT = '/var/www/public/';
var IMAGE_EXTENSIONS = [ 'png', 'jpg', 'jpeg', 'gif', 'ico' ];
var editor;
var preferences = { };

// bFileChanged is set by typing in editor window
// When a file is clicked in fileTree and bFileChanged is true, the save dialog is displayed
//  and execution pauses in an Interval loop, waiting for status to change
// If user chooses Save, status is set to 2, loop calls Save and sets status to 1. When
//  save completes, bFileChanged is set to false (which deals with the case when user clicks
//  normal Save button or types Cmd/Ctrl-S) and if status is 1, it is set to 0
// If user clicks Don't Save, bFileChanged is set to false and status to 0
// After a new file is loaded (which triggers a change), bFileChanged is set to false
var bTrackChanges = false;
var bFileChanged = false;

function trackChanges(enable) {
    if (enable) {
        bFileChanged = false;
        bTrackChanges = true;
    } else {
        bTrackChanges = false;
    }
}

// Sets global bFileChanged Boolean and indicator
function fileChanged () {
    if (bTrackChanges) {
        if (!bFileChanged) {
            bFileChanged = true;
            flagLocation();
        }
    }
}

// fileTree operations
function showPicture(path) {
    var rp = rascal.picture,
        fpath = path.split(ROOT).pop(),
        frp = $('#frame-p');
    console.log('showPicture ' + path);
    // Set up geometry and show frame
    setPictureFrameSize (frp);
    if (frp.css('visibility') !== 'visible') {
        frp.css('visibility', 'visible')
        .hide()
        .fadeTo('fast', 1);
    }
    // Set up picture
    if (DEBUG_ON_MAC) {
        rp.imgRoot = 'http://localhost:5000/';
    }
    rp.container = 'frame-p';
    rp.caption = 'location-bar';
    rp.show(fpath);
}

function hidePicture() {
    if (rascal.picture.showing) {
        $('#frame-p').css('visibility', 'hidden');
        rascal.picture.empty();
    }
}

// Clears file change indicator, saves path
function displayLocation(path) {
    "use strict";
    var fpath = path.split(ROOT).pop();
    var apath;
    if (fpath.match(/templates\//)) {
        apath = fpath.split('templates').pop();
        if (DEBUG_ON_MAC) {
            apath = 'http://localhost:5000/' + apath;
        }
        $('#location-bar').html('<a href="' + apath + '">' + fpath + '</a>');
    } else {
        $('#location-bar').text(fpath);
    }
    $('#path').val(fpath);
}

function flagLocation() {
    var lb;
    if (bFileChanged) {
        lb = $('#location-bar');
        lb.html(lb.html() + '&nbsp;◆');
    }
}

function clearLocation() {
    $('#location-bar').html('&nbsp;');
    $('#path').val('');
}

// Load a file into the edit buffer with optional save of existing changed file
// The load function is called synchronously with status = 0 if the previous file was not changed
// If it was changed, the save file dialog is displayed and load called asynchronously with status = -1
// If the user chooses to save the file, status is set to 2, saveFile is called and status lowered to 1
//  and, when the save completes, to 0
// If the user chooses not to save the file, status is set to 0
// When status = 0, the new picture or file is loaded and, for files, change tracking is resumed
loadFile = {
    path: '',
    status: -1,
    int_status: undefined,
    load: function () {
        var lf = loadFile, ext;
        if (lf.status === 2) {
            lf.status = 1;
            saveFile();
        } else if (lf.status === 0) {
            ext = lf.path.split('.').pop().toLowerCase();
            if ($.inArray(ext, IMAGE_EXTENSIONS) >= 0) {
                showPicture(lf.path);
            } else {
                hidePicture();
                $.post('/editor/read', 'path=' + lf.path.split(ROOT).pop(), function (response) {
                    editorSetText(response, ext);
                    displayLocation(loadFile.path);
                    trackChanges(true);
                });
            }
            if (lf.int_status !== undefined) {
                lf.int_status = clearInterval(lf.int_status);
            }
        } else {
            console.log('loadFile: waiting for user');
        }
    },
    init: function (path) {
        "use strict";
        var lf = loadFile;
        lf.path = path;
        if (bFileChanged) {
            $('#overlay-s').css('visibility', 'visible');
            $('#save-file-message').text('Save changes to "' + $('#path').val() + '"?');
            lf.status = -1;
            lf.int_status = setInterval(loadFile.load, 500);
        } else {
            lf.status = 0;
            lf.load();
        }
    }
}

$('#save-yes').click(function () {
    "use strict";
    loadFile.status = 2;
    $('#overlay-s').css('visibility', 'hidden');
});

$('#save-no').click(function () {
    "use strict";
    loadFile.status = 0;
    bFileChanged = false;
    $('#overlay-s').css('visibility', 'hidden');
});

// The fileTree callback function is called when the user clicks a file
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
        trackChanges(false);
        loadFile.init(path);
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
            flagLocation();
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
                trackChanges(false);
                clearLocation();                
                bFileChanged = false;
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
    $.post('/editor/save', { path: $('#path').val(), text: s }, function (response) {
        displayLocation($('#path').val());
        bFileChanged = false;
        if (loadFile.status === 1) {
            loadFile.status = 0;
        }
    });
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
