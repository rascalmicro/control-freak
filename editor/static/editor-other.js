// Support for resizing window - see also editor-resize.js

var resizeDelay = (function () {
    var timer = 0;
    return function(callback, ms) {
        clearTimeout (timer);
        timer = setTimeout(callback, ms);
    };
})();

// function adjustGeometry () {
//     var adjustSize = false, w, h, dw, dh;
//     if (adjustSize) {
//         w = $(window).width();
//         h = $(window).height();
//         dw = (w > 1290) ? w - 1290 : 0;
//         dh = (h > 765) ? h - 765 : 0;
//         $('.rascalcontent').width(1280 + dw);
//     }
// }

function adjustGeometry () {
    var w, h, dw, dh;
    if (ADJUSTSIZE) {
        w = $(window).width();
        h = $(window).height();
        console.log('size ' + w + ' x ' + h);
        dw = (w > (1260 + XW)) ? w - (1260 + XW) : 0;
        dh = (h > (637 + XH)) ? h - (637 + XH) : 0;
        console.log('resize ' + dw + ' x ' + dh);
        $('.rascalcontent').width(1260 + dw);
    }
}
