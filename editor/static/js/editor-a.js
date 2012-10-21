// Support for ACE
// JSLint 8 Oct 2012 jQuery $ applyTheme applyFontSize applyLineHeight applyTabSize applySoftTabs
// applyVisibleTabs applyLineWrapping applyLineNumbers applyMatchBrackets applyHighlightSelectedWord
// trackChanges editor ace editorSetMode fileChanged preferences

var prefs = {
    defaults: {
        theme: 'textmate',
        fontSize: 12,
        lineHeight: 1.4,
        tabSize: 4,
        softTabs: true,
        visibleTabs: false,
        lineWrapping: 0,
        lineNumbers: false,
        matchBrackets: false,
        highlightSelectedWord: false
    },
    types: {
        theme: 'string',
        fontSize: 'int',
        lineHeight: 'float',
        tabSize: 'int',
        softTabs: 'boolean',
        visibleTabs: 'boolean',
        lineWrapping: 'int',
        lineNumbers: 'boolean',
        matchBrackets: 'boolean',
        highlightSelectedWord: 'boolean'
    },
    apply: {
        theme: applyTheme,
        fontSize: applyFontSize,
        lineHeight: applyLineHeight,
        tabSize: applyTabSize,
        softTabs: applySoftTabs,
        visibleTabs: applyVisibleTabs,
        lineWrapping: applyLineWrapping,
        lineNumbers: applyLineNumbers,
        matchBrackets: applyMatchBrackets,
        highlightSelectedWord: applyHighlightSelectedWord
    }
};

function setPictureFrameSize(frp) {
    "use strict";
    frp.height($('#ace-editor').height())
        .width($('#ace-editor').width());
}

function initEditor() {
    trackChanges(false);
    editor = ace.edit("ace-editor");
    editor.setTheme("ace/theme/textmate");
    editorSetMode('txt');
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

function editorSetMode(ext) {
    "use strict";
    var Mode;
    switch (ext.toLowerCase()) {
    case 'css':
        Mode = ace.require("ace/mode/css").Mode;
        console.log('Mode css');
        break;
    case 'js':
        Mode = ace.require("ace/mode/javascript").Mode;
        console.log('Mode javascript');
        break;
    case 'py':
        Mode = ace.require("ace/mode/python").Mode;
        console.log('Mode python');
        break;
    case 'html':
        Mode = ace.require("ace/mode/html").Mode;
        console.log('Mode html');
        break;
    case 'xml':
        Mode = ace.require("ace/mode/xml").Mode;
        console.log('Mode xml');
        break;
    case 'less':
        Mode = ace.require("ace/mode/less").Mode;
        console.log('Mode less');
        break;
    case 'md':
        Mode = ace.require("ace/mode/markdown").Mode;
        console.log('Mode markdown');
        break;
    default:
        Mode = ace.require("ace/mode/text").Mode;
        console.log('Mode txt');
        break;
    }
    editor.getSession().setMode(new Mode());
    editor.setReadOnly(ext === 'log');
}

function editorSetText(s, ext) {
    "use strict";
    if (ext === undefined) {
        ext = 'txt';
    }
    editor.getSession().setValue(s);
    editorSetMode(ext);
}

function editorGetText() {
    "use strict";
    return editor.getSession().getValue();
}

function isReadOnly() {
    return editor.getReadOnly();
}

function initEditor() {
    trackChanges(false);
    editor = ace.edit("ace-editor");
    editor.setTheme("ace/theme/textmate");
    editorSetMode('txt');
    editor.getSession().on('change', fileChanged);
}


// Manage preferences
function applyTheme() {
    "use strict";
    console.log('applyTheme ' + preferences.theme.toLowerCase());
    editor.setTheme('ace/theme/' + preferences.theme.toLowerCase());
}

function applyFontSize() {
    "use strict";
    console.log('applyFontSize ' + preferences.fontSize);
    $('#ace-editor').css('font-size', preferences.fontSize + 'px');
}

function applyLineHeight() {
    "use strict";
    console.log('applyLineHeight ' + preferences.lineHeight);
    $('#ace-editor').css('line-height', preferences.lineHeight + 'em');
}

function applyTabSize() {
    "use strict";
    console.log('applyTabSize ' + preferences.tabSize);
    editor.getSession().setTabSize(preferences.tabSize);
}

function applySoftTabs() {
    "use strict";
    console.log('applySoftTabs ' + preferences.softTabs);
    editor.getSession().setUseSoftTabs(preferences.softTabs);
}

function applyVisibleTabs() {
    "use strict";
    console.log('applyVisibleTabs ' + preferences.visibleTabs);
    editor.renderer.setShowInvisibles(preferences.visibleTabs);
}

function applyLineWrapping() {
    "use strict";
    var lw = preferences.lineWrapping,
        es = editor.getSession();
    console.log('applyLineWrapping ' + lw);
    if (lw === 2) {
        es.setWrapLimitRange(80, 80);
        es.setUseWrapMode(true);
        editor.setShowPrintMargin(true);
    } else if (lw === 1) {
        es.setWrapLimitRange(null, null);
        es.setUseWrapMode(true);
        editor.setShowPrintMargin(false);
    } else {
        es.setUseWrapMode(false);
        editor.setShowPrintMargin(false);
    }
}

function applyLineNumbers() {
    "use strict";
    console.log('applyLineNumbers ' + preferences.lineNumbers);
    editor.renderer.setShowGutter(preferences.lineNumbers);
}

function applyMatchBrackets() {
    "use strict";
    console.log('applyMatchBrackets ' + preferences.matchBrackets);
    editor.setBehavioursEnabled(preferences.matchBrackets);
}

function applyHighlightSelectedWord() {
    "use strict";
    console.log('applyHighlightSelectedWord ' + preferences.highlightSelectedWord);
    editor.setHighlightSelectedWord(preferences.highlightSelectedWord);
}


function setTheme() {
    "use strict";
    preferences.theme = $(this).val();
    prefs.apply.theme();
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

function setLineWrapping() {
    "use strict";
    preferences.lineWrapping = parseInt($(this).val(), 10);
    // console.log('lineWrapping ' + preferences.lineWrapping);
    prefs.apply.lineWrapping();
}

function setLineNumbers() {
    "use strict";
    preferences.lineNumbers = $(this).is(':checked');
    prefs.apply.lineNumbers();
}

function setMatchBrackets() {
    "use strict";
    preferences.matchBrackets = $(this).is(':checked');
    prefs.apply.matchBrackets();
}

function setHighlightSelectedWord() {
    "use strict";
    preferences.highlightSelectedWord = $(this).is(':checked');
    prefs.apply.highlightSelectedWord();
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
    $('#wrapOff').click(setLineWrapping)
         .each(function () {
            this.checked = (preferences.lineWrapping === 0);
        });
    $('#wrapOn').click(setLineWrapping)
         .each(function () {
            this.checked = (preferences.lineWrapping === 1);
        });
    $('#wrap80').click(setLineWrapping)
         .each(function () {
            this.checked = (preferences.lineWrapping === 2);
        });
    $('#lineNumbers').click(setLineNumbers)
        .each(function () {
            this.checked = preferences.lineNumbers;
        });
    $('#matchBrackets').click(setMatchBrackets)
        .each(function () {
            this.checked = preferences.matchBrackets;
        });
    $('#highlightSelectedWord').click(setHighlightSelectedWord)
        .each(function () {
            this.checked = preferences.highlightSelectedWord;
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
    $.post('/editor/save_prefs', { section: 'Ace', prefs: JSON.stringify(preferences) }, function (response) {
        console.log('save_prefs ' + response);
    });
}

function defaultPreferences() {
    var pd = prefs.defaults, p;
    for (p in pd) {
        if (pd.hasOwnProperty(p)) {
            console.log('Restoring default ' + p + ': ' + pd[p]);
            preferences[p] = pd[p];
        }
    }
    applyAll();
    bindEditPreferences();
}

function initPreferences() {
    "use strict";
    $.post('/editor/read_prefs', { section: 'Ace', types: JSON.stringify(prefs.types),
            defaults: JSON.stringify(prefs.defaults)}, function (response) {
        preferences = JSON.parse(response);
        console.log('Init preferences ' + JSON.stringify(preferences));
        applyAll();
        bindEditPreferences();
    });
}
