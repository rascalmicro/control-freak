// var $, CodeMirror, rascal;

// Set up globals
var ROOT = '/var/www/public/';
var IMAGE_EXTENSIONS = [ 'png', 'jpg', 'jpeg', 'gif', 'ico' ];
var EXCEPTIONS = ['/var/www/public/server.py',
        '/var/www/public/static/', '/var/www/public/templates/']
var DEFAULT_PICTURE = 'static/images/picture_help.png'
var editor;
var preferences = { };

// bFileChanged is set by typing in editor window
// When a new file is clicked in fileTree and bFileChanged for the existing file is true,
//  the save dialog is displayed and execution pauses in an Interval loop, waiting for the
//  status to change
// If user chooses Save, the status is set to 2, the loop calls Save and sets status to 1.
//  When the save completes, bFileChanged is set to false (as it also does in the normal case when
//  user clicks Save button or types Cmd/Ctrl-S) and if status is 1, it is set to 0.
// If user clicks Don't Save, bFileChanged is set to false and status to 0
// After a new file is loaded (which triggers a change), bFileChanged is set to false
// A further subtlety is that the file or picture path is tracked in hidden input "path".
//   When a file or picture that is already loaded is clicked in the fileTree, it is ignored

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
function fileChanged() {
    if (bTrackChanges) {
        if (!bFileChanged) {
            bFileChanged = true;
            highlightChanged();
        }
    }
}

function highlightChanged() {
    var fpath = ROOT + $('#path').val();
    console.log('HighlightChanged ' + fpath);
    rascal.dnd.changedFile = fpath;
    $('LI A[rel="' + fpath + '"]').addClass('changed');
    $('#location-bar').addClass('changed');
    $('#location-bar A').addClass('changed');
}

function unhighlightChanged() {
    rascal.dnd.changedFile = undefined;
    $('LI A').removeClass('changed');
    $('#location-bar').removeClass('changed');
}

// fileTree operations
function showPicture(path) {
    var rp = rascal.picture,
        fpath = path.split(ROOT).pop(),
        frp = $('#frame-p');
    console.log('showPicture ' + fpath);
    if (!fpath.match(/static\//)) {
        fpath = DEFAULT_PICTURE;
    }
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
    $('#path').val(fpath);
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
    var apath = '#';
    if (fpath.match(/templates\//)) {
        apath = fpath.split('templates').pop();
        if (DEBUG_ON_MAC) {
            apath = 'http://localhost:5000' + apath;
        }
        $('#location-bar').html('<a href="' + apath + '">' + fpath + '</a>');
    } else {
        $('#location-bar').text(fpath);
    }
    $('#path').val(fpath);
}

function clearLocation() {
    "use strict";
    $('#location-bar').html('&nbsp;');
    $('#path').val('');
}

// Load a new picture or file. For files, change tracking is resumed
function loadFile(path) {
    "use strict";
    var ext = path.split('.').pop().toLowerCase();
    trackChanges(false);
    if ($.inArray(ext, IMAGE_EXTENSIONS) >= 0) {
        showPicture(path);  // NB Updates location and path
    } else {
        hidePicture();
        $.post('/editor/read', 'path=' + path.split(ROOT).pop(), function (response) {
            editorSetText(response, ext);
            displayLocation(path);
            trackChanges(true);
        });
    }
}

// Load something into the edit buffer with optional save of existing changed file
// The save file dialog is displayed and wait called asynchronously with status = -1
// If the user chooses to save the file, status is set to 2, saveFile is called and
// status lowered to 1 and then, when the save completes, to 0
// If the user chooses not to save the file, status is set to 0
// When status = 0, the callback function is executed
var SAVE = 0
var REVERT = 1;

querySave = {
    callback: function (status) {
         "use strict";
    },
    status: -1,
    int_status: undefined,
    wait: function () {
        var qs = querySave;
        if (qs.status === 3) {
            qs.status = 2;
            saveFile();
        } else if ((qs.status === 1) || (qs.status === 0)) {
            qs.int_status = clearInterval(qs.int_status);
            qs.callback(qs.status);
        } else {
            console.log('querySave: waiting for user');
        }
    },
    init: function (which, callback) {
        "use strict";
        var qs = querySave;
        qs.callback = callback;
        qs.status = -1;
        if (which === SAVE) {
            $('#modal-s').modal('show')
            // $('#overlay-s').css('visibility', 'visible');
            $('#save-file-message').html('Do you want to save the changes you made to the file "' + $('#path').val() + '"?<br/>Your changes will be lost if you don\'t save them.');
        } else {
            $('#modal-r').modal('show')
            // $('#overlay-r').css('visibility', 'visible');
            $('#revert-file-message').text('Are you sure you want to revert the file "' + $('#path').val() + '" to its original state?');
        }
        qs.int_status = setInterval(querySave.wait, 500);
        qs.wait();
    }
}

// The fileTree callback function is executed when the user clicks a file
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
        // If already loaded do nothing
        // console.log('New path ' + path.split(ROOT).pop());
        // console.log('Old path ' + $('#path').val());
        // if (path.split(ROOT).pop() !== $('#path').val()) {
            if (!bFileChanged) {
                loadFile(path);
            } else {
                var which;
                if (path.split(ROOT).pop() !== $('#path').val()) {
                    which = SAVE;
                } else {
                    which = REVERT;
                }
                querySave.init(which, function (status) {
                    if (status === 1) {
                        loadFile(path);
                    }
                });
            }
        // }
    });
}

// File or folder deletion
var FILE = 0;
var FOLDER = 1;

queryDelete = {
    callback: function (status) {
         "use strict";
    },
    status: -1,
    int_status: undefined,
    wait: function () {
        var qd = queryDelete;
        if ((qd.status === 1) || (qd.status === 0)) {
            qd.int_status = clearInterval(qd.int_status);
            qd.callback(qd.status);
        } else {
            console.log('queryDelete: waiting for user');
        }
    },
    init: function (which, path, callback) {
        "use strict";
        var qd = queryDelete;
        qd.callback = callback;
        qd.status = -1;
        $('#modal-d').modal('show')
        // $('#overlay-d').css('visibility', 'visible');
        if (which === FILE) {
            $('#delete-file-message').text('Are you sure you want to delete the file "' + path + '"?');
        } else {
            $('#delete-file-message').text('Are you sure you want to delete the folder "' + path + '"?');
        }
        qd.int_status = setInterval(queryDelete.wait, 500);
        qd.wait();
    }
}

var deleteFileBusy = false;     // Use semaphore to avoid repeated deletions

$('li.file').live('mouseenter mouseleave', function (event) {
    "use strict";
    var fpath;
    if (event.type === 'mouseenter') {
        fpath = $(this).children('a').attr('rel');
        $(this).children('a').addClass('selected');
        if ($.inArray(fpath, EXCEPTIONS) === -1) {
            $(this).children('img').addClass('selected');
            $(this).children('img').click(function () {
                var jqel, path;
                if (!deleteFileBusy) {
                    deleteFileBusy = true;
                    jqel = $(this).parent();
                    path = fpath.split(ROOT).pop();
                    queryDelete.init(FILE, path, function (status) {
                        if (status === 1) {
                            console.log('DELETE ' + path);
                            if (path === $('#path').val()) {
                                if (bFileChanged) {
                                    bFileChanged = false;
                                    unhighlightChanged();
                                }
                                trackChanges(false);
                                editorSetText('');
                                clearLocation();
                                hidePicture();
                            }
                            $.post('/editor/delete_file', { filename: path }, function (response) {
                                console.log('DELETE_FILE ' + response);
                                jqel.hide('slow');
                                saveMsg('Deleted file');
                            }).error(function (jqXHR, textStatus, errorThrown) {
                                console.log('DELETE_FILE: ' + textStatus + ': ' + errorThrown);
                                saveMsg('Delete file failed');
                            });
                        } else {
                            console.log('DELETE cancel');
                        }
                        deleteFileBusy = false;
                    });
                }
            });
        }
    } else {
        $(this).children('a').removeClass('selected');
        $(this).children('img').removeClass('selected');
    }
});

$('li.directory.expanded').live('mouseenter mouseleave', function (event) {
    "use strict";
    var fpath;
    if ($(this).children('ul').children().size() === 0) {
        if (event.type === 'mouseenter') {
            fpath = $(this).children('a').attr('rel');
            if ($.inArray(fpath, EXCEPTIONS) === -1) {
                $(this).children('a').addClass('selected');
                $(this).children('img').addClass('selected');
                $(this).children('img').click(function () {
                    var jqel, path;
                    if (!deleteFileBusy) {
                        deleteFileBusy = true;
                        jqel = $(this).parent();
                        path = fpath.split(ROOT).pop();
                        queryDelete.init(FOLDER, path, function (status) {
                            if (status === 1) {
                                console.log('DELETE ' + path);
                                $.post('/editor/delete_folder', { filename: path }, function (response) {
                                    console.log('DELETE_FOLDER ' + response);
                                    jqel.hide('slow');
                                    saveMsg('Deleted folder');
                                }).error(function (jqXHR, textStatus, errorThrown) {
                                    console.log('DELETE_FOLDER: ' + textStatus + ': ' + errorThrown);
                                    saveMsg('Delete folder failed');
                                });
                            } else {
                                console.log('DELETE cancel');
                            }
                            deleteFileBusy = false;
                        });
                    }
                });
            }
        } else {
            $(this).children('a').removeClass('selected');
            $(this).children('img').removeClass('selected');
        }
    }
});

$('li.directory.collapsed a.selected').live('mouseenter mouseleave', function (event) {
    "use strict";
    $(this).removeClass('selected');
    $(this).parent().children('img').removeClass('selected');
});

// Move a file or folder (initiated by DnD)
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
            if (bFileChanged) {
                highlightChanged();
            }
        }
    }).error(function (jqXHR, textStatus, errorThrown) {
        console.log('moveItem: ' + textStatus + ': ' + errorThrown);
        saveMsg('Move failed');
    });
}

function initRascalDnd() {
    "use strict";
    var rd = rascal.dnd;
    rd.root = ROOT;
    rd.container = 'filetree';
    rd.notDraggable = EXCEPTIONS;
    rd.itemDropped = moveItem;
    rd.filesDropped = uploadItems;
    rd.init();
}

// file operations
function saveProgress(pc) {
    console.log('progress ' + pc);
    $('#save-bar').css('width', (100 - pc) + '%');
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
    var p = $('#path').val();
    var s = editorGetText();
    $('#save-bar').css('width', '0%');
    if (rascal.picture.showing) {
        saveMsg('Can\'t save pictures');
    } else if (p === '') {
        saveMsg('Nothing to save');
    } else {
        console.log('saveFile: saving ' + p);
        $.post('/editor/save', { path: p, text: s }, function (response) {
            console.log('saveFile: ' + response);
            displayLocation($('#path').val());
            bFileChanged = false;
            unhighlightChanged();
            if (querySave.status === 2) {
                querySave.status = 1;
            }
        }).error(function (jqXHR, textStatus, errorThrown) {
            console.log('saveFile: ' + textStatus + ': ' + errorThrown);
        });
        $('#save-progress')
            .addClass('progress-striped')
            .addClass('active');
        $('#save-bar').animate({ 'width': '100%' }, 1000, function () {
            $('#save-progress')
                .removeClass('active')
                .removeClass('progress-striped');
            saveMsg('Saved file');
        });
    }
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
    $('#save-progress')
        .removeClass('active')
        .removeClass('progress-striped');
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

// chrome maps javascript files to text/javascript, firefox to application/x-javascript
function uploadInit(files, dst) {
    var ru = rascal.upload;
    // set up postUrl, allowed types, progress, status and complete
    ru.postUrl = '/editor/xupload';
    ru.allowedTypes = [ 'image/', 'text/html', 'text/css', 'text/javascript',
        'application/x-javascript', 'text/x-python-script' ];
    ru.progress = saveProgress;
    $('#save-bar').css('width', '0%')
    $('#save-progress')
        .addClass('progress-striped')
        .addClass('active');
    ru.status = uploadStatus;
    ru.complete = uploadComplete;
    trackChanges(false);
    clearLocation();
    editorSetText('');
    ru.filesDropped(files, dst.split(ROOT).pop());
}

function uploadItems(files, dst) {
    if (!bFileChanged) {
        uploadInit(files, dst);
    } else {
        querySave.init(SAVE, function (status) {
            if (status === 1) {
                uploadInit(files, dst);
            }
        });
    }
}

// dialog handling
$('#new-template').click(function () {
    "use strict";
    $('#modal-t').modal('show')
});

$('#modal-t').on('shown', function () {
    "use strict";
    $('#template-name').focus();
})

$('#create-template').click(function () {
    "use strict";
    var templateName = $('#template-name').val().trim();
    if (templateName !== '') {
        $.post('/editor/new_template', { templateName: templateName }, function (response) {
            console.log(response);
            displayTree('/var/www/public/templates/');
            $('#modal-t').modal('hide')
        }).error(function (jqXHR, textStatus, errorThrown) {
            console.log('new_template: ' + textStatus + ': ' + errorThrown);
            if (errorThrown === 'CONFLICT') {
                $('#template-message').text('Template exists - please use a different name')
                    .css('color', 'red');
            } else {    // 'Bad Request'
                $('#template-message').text('Template could not be created')
                    .css('color', 'red');
            }
            $('#template-name').focus();
        });
    } else {
        $('#template-name').focus();
    }
});

$('#cancel-template').click(function () {
    "use strict";
    $('#modal-t').modal('hide')
    // $('#overlay-t').css('visibility', 'hidden');
});

$('#new-folder').click(function () {
    "use strict";
    $('#modal-f').modal('show')
});

$('#modal-f').on('shown', function () {
    "use strict";
    $('#folder-name').focus();
})

$('#create-folder').click(function () {
    "use strict";
    var folderName = $('#folder-name').val().trim();
    if (folderName !== '') {
        $.post('/editor/new_folder', { folderName: folderName }, function (response) {
            console.log(response);
            displayTree('/var/www/public/static/');
            $('#modal-f').modal('hide')
        }).error(function (jqXHR, textStatus, errorThrown) {
            console.log('new_folder: ' + textStatus + ': ' + errorThrown);
            if (errorThrown === 'CONFLICT') {
                $('#folder-message').text('Folder exists - please use a different name')
                    .css('color', 'red');
            } else {    // 'Bad Request'
                $('#folder-message').text('Folder could not be created (mkdir returned an error)')
                    .css('color', 'red');
            }
            $('#folder-name').focus();
        });
    } else {
        $('#folder-name').focus();
    }
});

$('#cancel-folder').click(function () {
    "use strict";
    $('#modal-f').modal('hide')
});

function initPreferences () {
    "use strict";
    getPreferences();
    // Save and Delete warnings in this file
    bindEditPreferences();
}

$('#preferences').click(function () {
    "use strict";
    $('#reload-bar').css('width', '0%');
     // $('#overlay-p').css('visibility', 'visible');
     // console.log('Preferences ' + JSON.stringify(preferences));
});

$('#cancel-prefs').click(function () {
    "use strict";
     $('#overlay-p').css('visibility', 'hidden');
     console.log('Preferences ' + JSON.stringify(preferences));
});

$('#save-yes').click(function () {
    "use strict";
    querySave.status = 3;
    $('#modal-s').modal('hide')
});

$('#save-no').click(function () {
    "use strict";
    querySave.status = 1;
    bFileChanged = false;
    unhighlightChanged();
    $('#modal-s').modal('hide')
});

$('#save-cancel').click(function () {
    "use strict";
    querySave.status = 0;
    $('#modal-s').modal('hide')
});

$('#revert-yes').click(function () {
    "use strict";
    querySave.status = 1;
    bFileChanged = false;
    unhighlightChanged();
    $('#modal-r').modal('hide')
});

$('#revert-cancel').click(function () {
    "use strict";
    querySave.status = 0;
    $('#modal-r').modal('hide')
});

$('#delete-yes').click(function () {
    "use strict";
    queryDelete.status = 1;
    $('#modal-d').modal('hide')
});

$('#delete-cancel').click(function () {
    "use strict";
    queryDelete.status = 0;
    $('#modal-d').modal('hide')
});

// Reload pytronics
$('#reload').click(function () {
    "use strict";
    $('#reload-bar').css('width', '0%');
    $.post('/editor/reload', function (response) {
        $('#reload-progress')
            .addClass('progress-striped')
            .addClass('active');
        $('#reload-bar').animate({ 'width': '100%' }, 10000, function () {
            $('#reload-progress')
                .removeClass('active')
                .removeClass('progress-striped');
            saveMsg('Reloaded pytronics');
        });
    }).error(function (jqXHR, textStatus, errorThrown) {
        console.log('reload: ' + textStatus + ': ' + errorThrown);
        saveMsg('Reload pytronics failed');
    });
});
