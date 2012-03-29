// Support for ACE

// /var/www/public/static/images/progressbg_420.gif
function showPicture(path) {
    var rp = rascal.picture,
        fpath = path.split(ROOT).pop(),
        frp = $('#frame-p');
    console.log('showPicture ' + path);
    // Set up geometry
    frp.height($('#ace-editor').height())
        .width($('#ace-editor').width());
    if (frp.css('visibility') !== 'visible') {
        // $('#ace-editor').css('visibility', 'hidden');
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
        // $('#ace-editor').css('visibility', 'visible');
        rascal.picture.empty();
    }
}

function editorSetMode(ext) {
    "use strict";
    var mode;
    switch (ext.toLowerCase()) {
    case 'css':
        mode = ace.require("ace/mode/css").Mode;
        console.log('Mode css');
        break;
    case 'js':
        mode = ace.require("ace/mode/javascript").Mode;
        console.log('Mode javascript');
        break;
    case 'py':
        mode = ace.require("ace/mode/python").Mode;
        console.log('Mode python');
        break;
    case 'html':
        mode = ace.require("ace/mode/html").Mode;
        console.log('Mode html');
        break;
    case 'xml':
        mode = ace.require("ace/mode/xml").Mode;
        console.log('Mode xml');
        break;
    default:
        mode = ace.require("ace/mode/text").Mode;
        console.log('Mode txt');
        break;
    }
    editor.getSession().setMode(new mode());
}

function editorSetText(s, ext) {
    "use strict";
    if (ext === undefined) {
        ext = 'txt';
    }
    editor.getSession().setValue(s);
    editorSetMode(ext);
}

function editorGetText () {
    "use strict";
    return editor.getSession().getValue();
}

function initEditor() {
    editor = ace.edit("ace-editor");
    editor.setTheme("ace/theme/textmate");
    // editor.setTheme("ace/theme/cobalt");
    editorSetMode('txt');
    editor.setShowPrintMargin(false);
    editor.getSession().setUseWrapMode(true);
    editor.getSession().setWrapLimitRange(null, null);
//     editor.getSession().setWrapLimitRange(80, 80);
}

// Manage preferences
// if (!session.getUseWrapMode()) {
//     wrapModeEl.value = "off";
// } else {
//     wrapModeEl.value = session.getWrapLimitRange().min || "free";
// }
// 
// selectStyleEl.checked = editor.getSelectionStyle() == "line";
// themeEl.value = editor.getTheme();
// highlightActiveEl.checked = editor.getHighlightActiveLine();
// showHiddenEl.checked = editor.getShowInvisibles();
// showGutterEl.checked = editor.renderer.getShowGutter();
// showPrintMarginEl.checked = editor.renderer.getShowPrintMargin();
// highlightSelectedWordE.checked = editor.getHighlightSelectedWord();
// showHScrollEl.checked = editor.renderer.getHScrollBarAlwaysVisible();
// softTabEl.checked = session.getUseSoftTabs();
// behavioursEl.checked = editor.getBehavioursEnabled();

function setLineWrapping() {
    "use strict";
    var session = editor.getSession();
    preferences.lineWrapping = $(this).is(':checked');
    session.setUseWrapMode(preferences.lineWrapping);
}

function setLineNumbers() {
    "use strict";
    var renderer = editor.renderer;
    preferences.lineNumbers = $(this).is(':checked');
    renderer.setShowGutter(preferences.lineNumbers);
}

function setPrintMargin() {
    "use strict";
    var renderer = editor.renderer;
    preferences.printMargin = $(this).is(':checked');
    renderer.setShowPrintMargin(preferences.printMargin);
}

function setHighlightSelectedWord() {
    "use strict";
    preferences.highlightSelectedWord = $(this).is(':checked');
    editor.setHighlightSelectedWord(preferences.highlightSelectedWord);
}

// Will be moved to editor.js
function getPreferences () {
    var session = editor.getSession();
    var renderer = editor.renderer;
    preferences.lineWrapping = session.getUseWrapMode();
    preferences.lineNumbers = renderer.getShowGutter();
    preferences.printMargin = renderer.getShowPrintMargin();
    preferences.highlightSelectedWord = editor.getHighlightSelectedWord();
}
  
function bindEditPreferences () {
    "use strict";
    $('#lineWrapping').click(setLineWrapping)
        .each (function () {
            this.checked = preferences.lineWrapping;
        });
    $('#lineNumbers').click(setLineNumbers)
        .each (function () {
            this.checked = preferences.lineNumbers;
        });
    $('#printMargin').click(setPrintMargin)
        .each (function () {
            this.checked = preferences.printMargin;
        });
    $('#highlightSelectedWord').click(setHighlightSelectedWord)
        .each (function () {
            this.checked = preferences.highlightSelectedWord;
        });
}
