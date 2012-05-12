// Support for ACE

function setPictureFrameSize (frp) {
    "use strict";
    frp.height($('#ace-editor').height())
        .width($('#ace-editor').width());
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
    trackChanges(false);
    editor = ace.edit("ace-editor");
    editor.setTheme("ace/theme/textmate");
    // editor.setTheme("ace/theme/cobalt");
    editorSetMode('txt');
    editor.setShowPrintMargin(false);
    editor.getSession().setUseWrapMode(true);
    editor.getSession().setWrapLimitRange(null, null);
//     editor.getSession().setWrapLimitRange(80, 80);
    editor.getSession().on('change', fileChanged);
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
