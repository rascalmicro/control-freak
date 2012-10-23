/* Copyright (c) 2012 Richard Klancer <rpk@pobox.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE. */

/*global $ console */
var x = 0,
    y = 0,
    intervalID,
    INTERVAL_LENGTH = 200; // ms

// define console as a noop if not defined
if (typeof console === 'undefined') console = { log: function() {} };

function postJoystickPosition() {
  $.post('/joystick', { x: x, y: y });
}

function startSending() {
  intervalID = setInterval(postJoystickPosition, INTERVAL_LENGTH);
}

function stopSending() {
  // one last time
  postJoystickPosition(); 
  clearInterval(intervalID);
}

// draws "joystick", updates x and y
function joystickGo() {
  
  // Just do the dead simplest thing right now -- we have one draggable element, and no encapsulation

  var dragInfo = {},
      centerX,
      centerY,
      radialLimit,
      radialLimitSquared;

  function updatePosition(_x, _y) {
    x = _x / radialLimit;
    y = - _y / radialLimit;
    console.log(x,y); 
  }

  function centerKnob() {
    var $el = $(dragInfo.element),
        width = $('#background').width();

    $el.animate({
      left: width/2,
      top: width/2
    }, 200);
    updatePosition(0, 0);
  }

  function dragStart(evt) {
    dragInfo.dragging = true;
    evt.preventDefault();

    var $el = $(dragInfo.element),
        offset = $el.offset(),
        width = $el.width(),
        cx = offset.left + width/2 - centerX,
        cy = offset.top + width/2 - centerY;

    dragInfo.dx = evt.pageX - cx;
    dragInfo.dy = evt.pageY - cy;
    startSending();
  }

  function drag(evt) {
    if ( ! dragInfo.dragging ) return;
    evt.preventDefault();

    var $el = $(dragInfo.element),
        offset = $el.offset(),
        width = $el.width(),

        // find the current center of the element
        cx = offset.left + width/2 - centerX,
        cy = offset.top + width/2 - centerY,
        newcx = evt.pageX - dragInfo.dx,
        newcy = evt.pageY - dragInfo.dy,
        newRadiusSquared = newcx*newcx + newcy*newcy,
        scale;

    if (newRadiusSquared > radialLimitSquared) {
      scale = Math.sqrt( radialLimitSquared / newRadiusSquared );
      newcx *= scale;
      newcy *= scale;
    }

    updatePosition(newcx, newcy);

    offset.left += (newcx - cx);
    offset.top += (newcy - cy);

    $(dragInfo.element).offset(offset);
  }

  function dragEnd() {
    dragInfo.dragging = false;
    centerKnob();
    stopSending();
  }

  function adjustDimensions() {
    var $background = $('#background'),
        $knob = $('#knob'),
        offset = $background.offset(),
        width = $background.width();

    makeCircular($background);
    makeCircular($knob);

    centerX = width/2 + offset.left;
    centerY = width/2 + offset.top;
    radialLimit = (width - $knob.width()) / 2;
    radialLimitSquared = radialLimit * radialLimit;
  }

  function makeCircular($el) {
    var width = $el.width();
    // Android 2 browser doesn't seem to understand percentage border-radius, so we need to set it
    // via an inline style once we know the width
    $el.css({
      height: width,
      borderRadius: width/2
    });
  }

  function wrapForTouch(f) {
    return function(evt) {
      if (evt.originalEvent && evt.originalEvent.touches && evt.originalEvent.touches.length === 1) {
        evt.pageX = evt.originalEvent.touches[0].pageX;
        evt.pageY = evt.originalEvent.touches[0].pageY;
      }
      return f(evt);
    };
  }

  $(function() {
    var $background = $('#background'),
        $knob = $('#knob');

    adjustDimensions();
    dragInfo.element = $knob[0];

    $knob.bind('touchstart mousedown', wrapForTouch(dragStart));
    $(document).bind('touchmove mousemove', wrapForTouch(drag));
    $(document).bind('touchend mouseup', wrapForTouch(dragEnd));

    $background.bind('mousedown', function() { return false; });
    $(window).bind('resize', adjustDimensions);
  });

}

// and...go:

joystickGo();
