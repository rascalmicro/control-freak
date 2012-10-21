// Support for CodeMirror2
// JSLint 8 Oct 2012 jQuery $ applyTheme applyFontSize applyLineHeight applyTabSize
// applySoftTabs applyVisibleTabs applyIndentUnit applyLineNumbers applyHighlightActive
// applyLineWrapping applyMatchBrackets CodeMirror editor trackChanges fileChanged preferences

var prefs = {
    defaults: {
        theme: 'blackboard',
        fontSize: 12,
        lineHeight: 1.4,
        tabSize: 4,
        softTabs: true,
        visibleTabs: false,
        indentUnit: 4,
        lineNumbers: false,
        highlightActive: true,
        lineWrapping: false,
        matchBrackets: false
    },
    types: {
        theme: 'string',
        fontSize: 'int',
        lineHeight: 'float',
        tabSize: 'int',
        softTabs: 'boolean',
        visibleTabs: 'boolean',
        indentUnit: 'int',
        lineNumbers: 'boolean',
        highlightActive: 'boolean',
        lineWrapping: 'boolean',
        matchBrackets: 'boolean'
    },
    apply: {
        theme: applyTheme,
        fontSize: applyFontSize,
        lineHeight: applyLineHeight,
        tabSize: applyTabSize,
        softTabs: applySoftTabs,
        visibleTabs: applyVisibleTabs,
        indentUnit: applyIndentUnit,
        lineNumbers: applyLineNumbers,
        highlightActive: applyHighlightActive,
        lineWrapping: applyLineWrapping,
        matchBrackets: applyMatchBrackets
    }
};

function setPictureFrameSize(frp) {
    "use strict";
    frp.height($('.CodeMirror-scroll').height())
        .width($('.CodeMirror-scroll').width());
}

// Support for highlighting active line
var hlActive = false;
var hlLine = null;
var hlLineStyle = "activeline-default";

function activeline() {
    if (hlActive) {
        if (hlLine !== null) {
            editor.setLineClass(hlLine, null, null);
        } else {
            console.log('WARNING activeline: hlLine is null');
        }
        hlLine = editor.setLineClass(editor.getCursor().line, null, hlLineStyle);
    }
}

// Initialise editor with soft tabs
function softTabs(cm) {
    "use strict";
    var ch, ts, ns;
    if (cm.somethingSelected()) {
        cm.indentSelection("add");
    } else {
        ch = cm.coordsChar(cm.cursorCoords(true)).ch;
        ts = cm.getOption('tabSize');
        ns = ts - (ch % ts);
        // console.log('softTabs: inserting ' + ns + ' spaces');
        cm.replaceSelection(new Array(ns + 1).join(' '), "end");
    }
}

function initEditor() {
    trackChanges(false);
    editor = CodeMirror.fromTextArea(document.getElementById('code'), {
        mode: 'text', // text mode doesn't exist explicitly, but setting it provokes plain text by default
        theme: 'default',
        tabSize: 4,
        indentUnit: 4,
        indentWithTabs: false,
        extraKeys: {
            "Tab": softTabs
        },
        onCursorActivity: activeline,
//        electricChars: false,
        onChange: fileChanged
    });
    if (CodeMirror.version !== undefined) {
        console.log('CodeMirror version: ' + CodeMirror.version);
    } else {
        console.log('CodeMirror version: v2.33 or earlier');
    }
}

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
//     onDragEvent: null,
//     lineWrapping: false,
//     lineNumbers: false,
//     gutter: false,
//     fixedGutter: false,
//     firstLineNumber: 1,
//     readOnly: false,
//     dragDrop: true,
//     onChange: null,
//     onCursorActivity: null,
//     onGutterClick: null,
//     onHighlightComplete: null,
//     onUpdate: null,
//     onFocus: null, onBlur: null, onScroll: null,
//     matchBrackets: false,
//     workTime: 100,
//     workDelay: 200,
//     pollInterval: 100,
//     undoDepth: 40,
//     tabindex: null,
//     autofocus: null
//   };

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
    case 'less':
        mode = 'less';
        break;
    case 'md':
        mode = 'markdown';
        break;
    case 'log':
        mode = 'log';
        break;
    default:
        mode = 'text';
    }
    // console.log('mode ' + mode);
    editor.setOption('mode', mode);
    editor.setOption('readOnly', (ext === 'log'));
}

function editorSetText(s, ext) {
    "use strict";
    if (ext === undefined) {
        ext = 'txt';
    }
    // Fix to ensure activeLine is updated when loading a new file
    editor.setValue(' ');
    editor.setCursor(0, 1);
    // End fix
    editor.setValue(s);
    editorSetMode(ext);
}

function editorGetText() {
    "use strict";
    return editor.getValue();
}

function isReadOnly() {
    return editor.getOption('readOnly');
}

var THEMES = ['default', 'night', 'solarized-light', 'solarized-dark'];

// Manage preferences
function applyTheme() {
    "use strict";
    var oldTheme = editor.getOption('theme'),
        newTheme;
    // console.log('applyTheme ' + preferences.theme);
    editor.setOption('theme', preferences.theme);
    // Set theme for other panes
    if ($.inArray(preferences.theme, THEMES) >= 0) {
        newTheme = preferences.theme;
    } else {
        newTheme = 'blackboard';
    }
    $('#ft-background')
        .removeClass('rm-well-' + oldTheme)
        .addClass('rm-well-' + newTheme);
    $('#filetree')
        .removeClass('filetree-' + oldTheme)
        .addClass('filetree-' + newTheme);
    $('#new-file-folder-bar')
        .removeClass('rm-well-' + oldTheme)
        .addClass('rm-well-' + newTheme);
    $('#location-bar')
        .removeClass('rm-well-' + oldTheme)
        .addClass('rm-well-' + newTheme);

    // Set active line highlight color
    hlLineStyle = 'activeline-' + newTheme;
    // console.log('+ hlLineStyle ' + hlLineStyle);
    if (preferences.highlightActive) {
        if (hlLine !== null) {
            activeline();
        }
    }

}

function applyFontSize() {
    "use strict";
    // console.log('applyFontSize ' + preferences.fontSize);
    $('.CodeMirror').css('font-size', preferences.fontSize + 'px');
}

function applyLineHeight() {
    "use strict";
    // console.log('applyLineHeight ' + preferences.lineHeight);
    $('.CodeMirror').css('line-height', preferences.lineHeight + 'em');
}

function applyTabSize() {
    "use strict";
    // console.log('applyTabSize ' + preferences.tabSize);
    editor.setOption('tabSize', preferences.tabSize);
}

function applySoftTabs() {
    "use strict";
    var ek = editor.getOption('extraKeys');
    // console.log('applySoftTabs ' + preferences.softTabs);
    if (ek !== null) {
        if (ek.Tab !== null) {
            // console.log('+ deleting tab property');
            delete ek.Tab;
        }
        if (preferences.softTabs) {
            // console.log('+ adding tab property softTabs');
            ek.Tab = softTabs;
        }
        editor.setOption('extraKeys', ek);
    } else {
        if (preferences.softTabs) {
            // console.log('+ creating tab property softTabs');
            editor.setOption('extraKeys', {'Tab': softTabs});
        }
    }
    // console.log('+ set indentWithTabs ' + !preferences.softTabs);
    editor.setOption('indentWithTabs', !preferences.softTabs);
}

function applyVisibleTabs() {
    "use strict";
    // console.log('applyVisibleTabs ' + preferences.visibleTabs);
    if (preferences.visibleTabs) {
        $('.CodeMirror').addClass('visibleTabs');
    } else {
        $('.CodeMirror').removeClass('visibleTabs');
    }
}

function applyIndentUnit() {
    "use strict";
    // console.log('applyIndentUnit ' + preferences.indentUnit);
    editor.setOption('indentUnit', preferences.indentUnit);
}

function applyLineNumbers() {
    "use strict";
    // console.log('applyLineNumbers ' + preferences.lineNumbers);
    editor.setOption('lineNumbers', preferences.lineNumbers);
}

function applyHighlightActive() {
    "use strict";
    // console.log('applyHighlightActive ' + preferences.highlightActive);
    if (preferences.highlightActive !== hlActive) {
        hlActive = preferences.highlightActive;
        if (hlActive) {
            // console.log('+ turning on hlActive');
            hlLine = editor.setLineClass(editor.getCursor().line, null, hlLineStyle);
        } else {
            // console.log('+ turning off hlActive');
            // Clear current highlight
            if (hlLine !== null) {
                editor.setLineClass(hlLine, null, null);
            } else {
                console.log('+ WARNING hlLine is null');
            }
        }
    }
}

function applyLineWrapping() {
    "use strict";
    // console.log('applyLineWrapping ' + preferences.lineWrapping);
    editor.setOption('lineWrapping', preferences.lineWrapping);
}

function applyMatchBrackets() {
    "use strict";
    // console.log('applyMatchBrackets ' + preferences.matchBrackets);
    editor.setOption('matchBrackets', preferences.matchBrackets);
}


function setTheme() {
    "use strict";
    preferences.theme = $(this).val();
    prefs.apply.theme();
    // editor.refresh();   // CodeMirror needs this to recalculate layout
}

function setFontSize() {
    "use strict";
    preferences.fontSize = $(this).val();
    prefs.apply.fontSize();
}

function setLineHeight() {
    "use strict";
    preferences.lineHeight = $(this).val();
    prefs.apply.lineHeight();
}

function setTabSize() {
    "use strict";
    preferences.tabSize = parseInt($(this).val(), 10);
    prefs.apply.tabSize();
}

function setSoftTabs() {
    "use strict";
    preferences.softTabs = $(this).is(':checked');
    prefs.apply.softTabs();
}

function setVisibleTabs() {
    "use strict";
    preferences.visibleTabs = $(this).is(':checked');
    prefs.apply.visibleTabs();
}

function setIndentUnit() {
    "use strict";
    preferences.indentUnit = parseInt($(this).val(), 10);
    prefs.apply.indentUnit();
}

function setLineNumbers() {
    "use strict";
    preferences.lineNumbers = $(this).is(':checked');
    prefs.apply.lineNumbers();
}

function setHighlightActive() {
    "use strict";
    preferences.highlightActive = $(this).is(':checked');
    prefs.apply.highlightActive();
}

function setLineWrapping() {
    "use strict";
    preferences.lineWrapping = $(this).is(':checked');
    prefs.apply.lineWrapping();
}

function setMatchBrackets() {
    "use strict";
    preferences.matchBrackets = $(this).is(':checked');
    prefs.apply.matchBrackets();
}

function bindEditPreferences() {
    "use strict";
    $('#theme').change(setTheme)
        .each(function () {
            $(this).val(preferences.theme);
        });
    $('#fontSize').change(setFontSize)
        .each(function () {
            this.value = preferences.fontSize;
        });
    $('#lineHeight').change(setLineHeight)
        .each(function () {
            this.value = preferences.lineHeight;
        });
    $('#tabSize').change(setTabSize)
        .each(function () {
            this.value = preferences.tabSize;
        });
    $('#softTabs').change(setSoftTabs)
        .each(function () {
            this.checked = preferences.softTabs;
        });
    $('#visibleTabs').change(setVisibleTabs)
        .each(function () {
            this.checked = preferences.visibleTabs;
        });
    $('#indentUnit').change(setIndentUnit)
        .each(function () {
            this.value = preferences.indentUnit;
        });
    $('#lineNumbers').click(setLineNumbers)
        .each(function () {
            this.checked = preferences.lineNumbers;
        });
    $('#highlightActive').click(setHighlightActive)
        .each(function () {
            this.checked = preferences.highlightActive;
        });
    $('#lineWrapping').click(setLineWrapping)
        .each(function () {
            this.checked = preferences.lineWrapping;
        });
    $('#matchBrackets').click(setMatchBrackets)
        .each(function () {
            this.checked = preferences.matchBrackets;
        });
}

function applyAll() {
    var pa = prefs.apply, f;
    for (f in pa) {
        if (pa.hasOwnProperty(f)) {
            pa[f]();
        }
    }
}

function savePreferences() {
    "use strict";
    $.post('/editor/save_prefs', { section: 'CodeMirror', prefs: JSON.stringify(preferences) }, function (response) {
        // console.log('save_prefs ' + response);
    });
}

function defaultPreferences() {
    var pd = prefs.defaults, p;
    for (p in pd) {
        if (pd.hasOwnProperty(p)) {
            // console.log('Restoring default ' + p + ': ' + pd[p]);
            preferences[p] = pd[p];
        }
    }
    applyAll();
    bindEditPreferences();
}

function initPreferences() {
    "use strict";
    $.post('/editor/read_prefs', { section: 'CodeMirror', types: JSON.stringify(prefs.types),
            defaults: JSON.stringify(prefs.defaults)}, function (response) {
        preferences = JSON.parse(response);
        applyAll();
        bindEditPreferences();
    });
}
