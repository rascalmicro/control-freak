/* 27 Jun 2012 dsmall for rascal-1.03 (trap error when no folder */

// Uncomment next line for JSLint
// var $, rascal, console, clearInterval, setInterval;

var slideChanging = false;

function loadPictures() {
    "use strict";
    $.post("/list-directory", { directory: 'static/pictures/' }, function (response) {
        var result, slideshow, sfname, i;
        result = $.parseJSON(response);
        console.log("loadPictures length " + result.length);
        // Clear existing pictures
        slideshow = $('#slideshow');
        slideshow.children().remove();
        // If any pictures have been found
        if (result.length) {
            // Werkzeug secure_filename replaces spaces with underscores
            sfname = rascal.upload.lastUpload.replace(/ /g, '_');
            // Add images from the pictures folder
            for (i = 0; i < result.length; i += 1) {
                console.log(result[i]);
                slideshow.append('<img src="/static/pictures/' + result[i] + '" />');
                if (result[i] === sfname) {
                    console.log(sfname + " -> active");
                    $('#slideshow IMG:last').addClass('active');
                }
            }
            // We need one picture to be active (also makes it visible)
            if ($('#slideshow IMG.active').length === 0) {
                $('#slideshow IMG:first').addClass('active');
            }
            $('#intro').css('visibility', 'visible');
        } else {
            $('#intro').css('visibility', 'hidden');
            $('#slideshow').append('<p id="dropmsg">Drop your pictures here</p>');
        }
        // If less than two pictures, hide the buttons
        if (result.length < 2) {
            $('#buttons').css('visibility', 'hidden');
        } else {
            $('#buttons').css('visibility', 'visible');
        }
    }).error(function (jqXHR, textStatus, errorThrown) {
        if (errorThrown === 'NOT FOUND') {
            $('#intro').css('visibility', 'hidden');
            $('#slideshow').append('<p id="dropmsg">Please create pictures folder<br/>in the static directory</p>');
        }
    });
}

function nextSlidePlease(direction) {
    "use strict";
    var $active, $next;
    direction = arguments.length > 0 ? direction : 1;
    $active = $('#slideshow IMG.active');
    if ($active.length === 0) {
        $active = $('#slideshow IMG:last');
    }
    // Show the images in the order they appear in the picture frame
    // Find the next slide forwards or backwards
    if (direction > 0) {
        // If moving forwards, roll over from last to first
        $next =  $active.next().length ? $active.next()
            : $('#slideshow IMG:first');
    } else {
        // Else if moving backwards roll over to last
        $next =  $active.prev().length ? $active.prev()
            : $('#slideshow IMG:last');
    }
    // Flag the current slide
    $active.addClass('last-active');
    slideChanging = true;
    // Hide the next slide, then make it active and dissolve into it
    $next.css({opacity: 0.0})
        .addClass('active')
        .animate({opacity: 1.0}, 1000, function () {
            $active.removeClass('active last-active');
            slideChanging = false;
        });
}

/* Control buttons */
// The interval timer is set when the slideshow is running
var int_timer;

function stopShow() {
    "use strict";
    // Also sets int_timer to undefined
    int_timer = clearInterval(int_timer);
    $('#auto').removeClass('btn-danger').addClass('btn-primary');
    $('#auto-icon').removeClass('icon-stop').addClass('icon-play');
    console.log('Slide show stop');
}

$('#next').click(function () {
    "use strict";
    if (!slideChanging) {
        if (int_timer) {
            stopShow();
        }
        nextSlidePlease(1);
    }
});

$('#previous').click(function () {
    "use strict";
    if (!slideChanging) {
        if (int_timer) {
            stopShow();
        }
        nextSlidePlease(-1);
    }
});

$('#auto').click(function () {
    "use strict";
    if (int_timer === undefined) {
        int_timer = setInterval(nextSlidePlease, 5000);
        $('#auto').removeClass('btn-primary').addClass('btn-danger');
        $('#auto-icon').removeClass('icon-play').addClass('icon-stop');
        console.log('Slide show start ' + int_timer);
    } else {
        stopShow();
    }
});

// glue between rascal.dnd and rascal.upload
function uploadProgress(pc) {
    // console.log('progress ' + pc);
    $('#progress').css('background-position', pc + '% 0').css('opacity', 1);
}

function uploadStatus (msg) {
    $('#status').html($('#status').html() + msg + '<br />');
}

function uploadComplete() {
    $('#progress').fadeTo(2000, 0);
    loadPictures();
}

function uploadItems(files, dst) {
    var ru = rascal.upload;
    // set up allowed types, progress, status and complete
    ru.allowedTypes = [ 'image/' ];
    ru.progress = uploadProgress;
    ru.status = uploadStatus;
    ru.complete = uploadComplete;
    $('#status').html('');
    ru.filesDropped(files, dst);
}


