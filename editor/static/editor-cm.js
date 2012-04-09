// Support for CodeMirror2

function setPictureFrameSize (frp) {
    "use strict";
    frp.height($('.CodeMirror-scroll').height())
        .width($('.CodeMirror-scroll').width());
}

function editorSetMode(ext) {
    "use strict";
    var mode;
    switch (ext.toLowerCase()) {
    case 'css':
        mode = 'css';
        break;
   case 'js':
        mode = 'javascript';
        break;
    case 'py':
        mode = 'python';
        break;
    case 'html':
    case 'xml':
        mode = 'htmlmixed';
        break;
    default:
        mode = 'text';
    }
    console.log('mode ' + mode);
    editor.setOption('mode', mode);
}

function editorSetText(s, ext) {
    "use strict";
    if (ext === undefined) {
        ext = 'txt';
    }
    editor.setValue(s);
    editorSetMode(ext);
}

function editorGetText() {
    "use strict";
    return editor.getValue();
}

function initEditor() {
    editor = CodeMirror.fromTextArea(document.getElementById('code'), {
        mode: 'text', // text mode doesn't exist explicitly, but setting it provokes plain text by default
        theme: 'night',
        tabSize: 4,
        indentUnit: 4,
//         enterMode: 'keep',
        electricChars: false,
        onChange: fileChanged,
        lineWrapping: true
    });
}

// Manage preferences
//   CodeMirror.defaults = {
//     value: "",
//     mode: null,
//     theme: "default",
//     indentUnit: 2,
//     indentWithTabs: false,
//     smartIndent: true,
//     tabSize: 4,
//     keyMap: "default",
//     extraKeys: null,
//     electricChars: true,
//     autoClearEmptyLines: false,
//     onKeyEvent: null,
//     lineWrapping: false,
//     lineNumbers: false,
//     gutter: false,
//     fixedGutter: false,
//     firstLineNumber: 1,
//     readOnly: false,
//     onChange: null,
//     onCursorActivity: null,
//     onGutterClick: null,
//     onHighlightComplete: null,
//     onUpdate: null,
//     onFocus: null, onBlur: null, onScroll: null,
//     matchBrackets: false,    // Doesn't work for big spans
//     workTime: 100,
//     workDelay: 200,
//     pollInterval: 100,
//     undoDepth: 40,
//     tabindex: null,
//     document: window.document
//   };

function setLineWrapping() {
    "use strict";
    preferences.lineWrapping = $(this).is(':checked');
    editor.setOption('lineWrapping', preferences.lineWrapping);
    editor.refresh();   // CodeMirror needs this to recalculate layout
}

function setLineNumbers() {
    "use strict";
    preferences.lineNumbers = $(this).is(':checked');
    editor.setOption('lineNumbers', preferences.lineNumbers);
    editor.refresh();   // CodeMirror needs this to recalculate layout
}

function getPreferences () {
    preferences.lineWrapping = editor.getOption('lineWrapping');
    preferences.lineNumbers = editor.getOption('lineNumbers');
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
}
