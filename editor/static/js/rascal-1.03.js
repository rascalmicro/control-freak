/* Library started by dsmall 2012 v1.03 */
// JSLint 6 Oct 2012 jQuery $

// NB Event handlers need to be named and static to avoid duplication

var rascal = {
    // Add drag and drop to jquery.filetree
    dnd: {
        root: '/var/www/public/',
        container: 'filetree',
        notDraggable: [],
        changedFile: undefined,
        itemDropped: function (src, dst) {
            "use strict";
        },
        filesDropped: function (files, dst) {
            "use strict";
        },
        handleDragStart: function (evt) {
            "use strict";
            evt.dataTransfer.effectAllowed = 'copy';
            evt.dataTransfer.setData('Text', this.rel);
            // console.log('dragstart ' + this.rel);
        },
        handleDragOver: function (evt) {
            "use strict";
            evt.stopPropagation();
            evt.preventDefault();
            evt.dataTransfer.dropEffect = 'copy';
            if (this.id === rascal.dnd.container) {
                $(this).addClass('dragover');
            } else {
                $(this).children('A').addClass('dragover');
            }
        },
        handleDrop: function (evt) {
            "use strict";
            var src, srcDir, dst;
            evt.stopPropagation();
            evt.preventDefault();
            if (this.id === rascal.dnd.container) {
                dst = rascal.dnd.root;
            } else {
                dst = this.querySelector('a').rel;
            }
            if (evt.dataTransfer) {
                src = evt.dataTransfer.getData('Text');
                if ((src !== 'undefined') && (src !== '')) {
                    srcDir = src.match(/.*\//)[0];
                    if (srcDir !== dst) {
                        console.log('handleDrop mv ' + src + ' to ' + dst);
                        rascal.dnd.itemDropped(src, dst);
                    } else {
                        console.log('handleDrop do nothing ' + src + ' to ' + dst);
                    }
                } else if (evt.dataTransfer.files) {
                    console.log('dropped files to ' + dst);
                    rascal.dnd.filesDropped(evt.dataTransfer.files, dst);
                }
            } else if (evt.target.files) {
                console.log('choose files to ' + dst);
                rascal.dnd.filesDropped(evt.target.files, dst);
            }
            if (this.id === rascal.dnd.container) {
                $(this).removeClass('dragover');
            } else {
                $(this).children('A').removeClass('dragover');
            }
        },
        handleDragLeave: function (evt) {
            "use strict";
            evt.stopPropagation();
            evt.preventDefault();
            if (this.id === rascal.dnd.container) {
                $(this).removeClass('dragover');
            } else {
                $(this).children('A').removeClass('dragover');
            }
        },
        init: function () {
            "use strict";
            var el;
            el = document.getElementById(rascal.dnd.container);
            el.addEventListener('dragover', rascal.dnd.handleDragOver, false);
            el.addEventListener('drop', rascal.dnd.handleDrop, false);
            el.addEventListener('dragleave', rascal.dnd.handleDragLeave, false);
        },
        bindTree: function (t) {
            "use strict";
            var el, dragItems, dragTargets, i;
            // Make all items draggable except for those in notDraggable array
            $(t).find('LI A').attr('draggable', function () {
                if ($.inArray(this.rel, rascal.dnd.notDraggable) >= 0) {
                    return undefined;
                }
                // console.log('draggable ' + this.rel);
                return 'true';
            });
            // Translate from jQuery to DOM so that we can use native HTML5 dnd
            $(t).addClass("bindTree");
            el = document.querySelector('.bindTree');
            $(t).removeClass("bindTree");
            // Set up a dragstart listener on all draggable elements
            dragItems = el.querySelectorAll('[draggable=true]');
            for (i = 0; i < dragItems.length; i += 1) {
                dragItems[i].addEventListener('dragstart', rascal.dnd.handleDragStart, false);
            }
            // Set up dragover, drop and dragleave listeners on all directory targets
            // dragTargets = el.querySelectorAll('.directory > a');
            dragTargets = el.querySelectorAll('.directory');
            for (i = 0; i < dragTargets.length; i += 1) {
                // console.log('dragtarget ' + dragTargets[i].rel);
                dragTargets[i].addEventListener('dragover', rascal.dnd.handleDragOver, false);
                dragTargets[i].addEventListener('drop', rascal.dnd.handleDrop, false);
                dragTargets[i].addEventListener('dragleave', rascal.dnd.handleDragLeave, false);
            }
            if (rascal.dnd.changedFile !== undefined) {
                $('LI A[rel="' + rascal.dnd.changedFile + '"]').addClass('changed');
            }
        }
    },
    // Support for file upload
    upload: {
        postUrl: '/xupload',
        directory: 'static/uploads/',
        allowedTypes: [ 'image/' ],
        maxFileBytes: 1024 * 1024,
        timeout: 40,
        totalBytes: 0,
        loadedBytes: 0,
        files: [],
        nextFile: -1,
        int_inFlight: undefined,
        inFlight: 0,
        inflightXhr: undefined,
        countDown: 0,
        lastUpload: '',
        progress: function (pc) {
            "use strict";
        },
        status: function (msg) {
            "use strict";
            console.log('rascal.upload: ' + msg);
        },
        complete: function (directory) {
            "use strict";
            console.log('rascal.upload: complete');
        },
        // This uploads a file asynchronously, returning before complete
        // There are handlers for progress and status messages
        uploadFile: function (file) {
            "use strict";
            var xhr = new XMLHttpRequest();
            if (xhr.upload) {
                // Listen to progress and update bar
                xhr.upload.addEventListener('progress', function (e) {
                    if (e.lengthComputable) {
                        // var pc = parseInt(100 - (e.loaded / e.total * 100), 10);
                        var pc = parseInt(100 - ((rascal.upload.loadedBytes + e.loaded) / rascal.upload.totalBytes * 100), 10);
                        rascal.upload.progress(pc);
                    }
                }, false);
                // File received/failed
                xhr.onreadystatechange = function () {
                    // State 4 indicates data transfer complete
                    if (xhr.readyState === 4) {
                        if (xhr.status === 200) {
                            // rascal.upload.status(' - success', 1);
                            rascal.upload.loadedBytes += file.size;
                            // console.log('Upload complete ' + file.name);
                            rascal.upload.lastUpload = file.name;
                        } else if (xhr.status === 0) {
                            rascal.upload.status('Upload of ' + file.name + ' aborted');
                        } else {
                            rascal.upload.status('Upload of ' + file.name +
                                ' failed (' + xhr.status + ' ' + xhr.statusText + ')');
                        }
                        rascal.upload.inFlight = 0;
                    }
                };
                // Start upload
                try {
                    xhr.open('POST', rascal.upload.postUrl, true);
                    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
                    xhr.setRequestHeader('X-File-Name', file.name);
                    xhr.setRequestHeader('X-Folder', rascal.upload.directory);
                    // Set Content-type
                    // Safari sets it to application/x-www-form-urlencoded
                    //   need to override because this causes Werkzeug to parse the stream
                    // Firefox sets it to file type
                    // Chrome leaves it blank
                    // Force Content-Type to file.type like Firefox
                    xhr.setRequestHeader('Content-Type', file.type);
                    xhr.send(file);
                    rascal.upload.inFlight = 1;
                    rascal.upload.inflightXhr = xhr;
                    // console.log('Upload sent ' + file.name);
                } catch (err) {
                    alert('XMLHttpRequest error ' + err.description);
                }
            } else {
                alert("Sorry, XMLHttpRequest upload doesn't seem to be supported by your browser.");
            }
        },
        uploadFiles: function () {
            "use strict";
            var ru = rascal.upload, f;
            if (ru.inFlight <= 0) {
                ru.nextFile += 1;
                if (ru.nextFile < ru.files.length) {
                    f = ru.files[ru.nextFile];
                    // ru.status('Uploading ' + f.name);
                    ru.countDown = ru.timeout;
                    ru.uploadFile(f);
                } else {
                    ru.int_inFlight = clearInterval(ru.int_inFlight);
                    ru.complete(ru.directory);
                }
            } else {
                ru.countDown -= 1;
                console.log('Waiting for file ' + ru.nextFile + ' (' + ru.countDown + ')');
                if (ru.countDown <= 0) {
                    ru.status('Timed out while uploading');
                    ru.inflightXhr.abort();
                }
            }
        },
        filesDropped: function (files, dst) {
            "use strict";
            var ru = rascal.upload, i, f;
            function isAllowed(ft) {
                var j;
                for (j = 0; j < ru.allowedTypes.length; j += 1) {
                    if (ft.indexOf(ru.allowedTypes[j]) === 0) {
                        return true;
                    }
                }
                return false;
            }
            ru.files = [];
            ru.directory = dst;
            ru.totalBytes = 0;
            ru.loadedBytes = 0;
            ru.lastUpload = '';
            for (i = 0; i < files.length; i += 1) {
                f = files[i];
                // Validate file type and size
                if (!isAllowed(f.type)) {
                    ru.status(f.name + ' (' + f.type + ') isn\'t a file type that can be uploaded');
                } else if (f.size >= ru.maxFileBytes) {
                    ru.status(f.name + ' (' + f.type + ') is too large (limit is ' +
                            ru.maxFileBytes / (1024 * 1024) + ' MB)', 1);
                } else {
                    ru.totalBytes += f.size;
                    ru.files.push(f);
                }
            }
            if (ru.files.length > 0) {
                ru.progress(100);
                ru.nextFile = -1;
                // console.log('totalBytes ' + ru.totalBytes);
                ru.uploadFiles();
                ru.int_inFlight = setInterval(rascal.upload.uploadFiles, 500);
            }
        }
    },
    // Support for directory functions
    directory: {
        directory: 'static/uploads',
        listID: 'filelist',
        // Convert returned JSON object into an array, allowing use of join
        listDirectory: function () {
            "use strict";
            $.post("/list-directory", { directory: rascal.directory.directory }, function (response) {
                var results = Array.prototype.slice.call($.parseJSON(response));
                $('#' + rascal.directory.listID).html(results.join('<br />'));
            }).error(function (jqXHR, textStatus, errorThrown) {
                if (errorThrown === 'NOT FOUND') {
                    $('#' + rascal.directory.listID).html('Folder "' + rascal.directory.directory + '" not found');
                }
            });
        },
        // Clear directory then list it
        clearDirectory: function (cf) {
            "use strict";
            if (cf !== undefined) {
                $.post("/clear-directory", { directory: rascal.directory.directory }, function (response) {
                    cf();
                });
            } else {
                $.post("/clear-directory", { directory: rascal.directory.directory });
            }
        }
    },
    // Support for picture scaling
    picture: {
        imgRoot: '/',
        container: '',
        caption: '',
        gap: 50,
        naturalWidth: 0,
        naturalHeight: 0,
        showing: false,
        show: function (fpath) {
            "use strict";
            var rp = rascal.picture, rpc, img;
            rpc = '#' + rp.container;
            $(rpc).children().remove();
            $(rpc).append('<img />');
            img = $(rpc + ' > img');
            img.hide();
            img.load(function () {
                var rp = rascal.picture;
                rp.naturalWidth = img[0].naturalWidth;
                rp.naturalHeight = img[0].naturalHeight;
                console.log('nw=' + rp.naturalWidth + ', nh=' + rp.naturalHeight);
                if (rp.caption !== '') {
                    $('#' + rp.caption).text(fpath + ' (' + rp.naturalWidth + ' x ' + rp.naturalHeight + ')');
                }
                rp.resize();
            });
            console.log('img src=' + rp.imgRoot + fpath);
            img.attr('src', rp.imgRoot + fpath);
        },
        resize: function () {
            "use strict";
            var rp = rascal.picture,
                fw = $('#' + rp.container).width(),
                fh = $('#' + rp.container).height(),
                img = $('#' + rp.container + ' > img'),
                gap = rp.gap,
                nw = rp.naturalWidth,
                nh = rp.naturalHeight,
                ww,
                wh;
            ww = nw;
            wh = nh;
            if (nw > (fw - gap)) {
                ww = fw - gap;
                wh = wh * (ww / nw);
                nh = wh;
                console.log('width scaled ww=' + ww + ', wh=' + wh);
            }
            if (nh > (fh - gap)) {
                wh = fh - gap;
                ww = ww * (wh / nh);
                console.log('height scaled ww=' + ww + ', wh=' + wh);
            }
            ww = parseInt(ww, 10);
            wh = parseInt(wh, 10);
            console.log('ww=' + ww + ', wh=' + wh);
            img.width(ww)
                .height(wh)
                .css('margin-top', parseInt((fh - wh) * 0.38, 10) + 'px')
                .css('margin-left', parseInt((fw - ww) * 0.5, 10) + 'px')
                .fadeIn('fast');
            rp.showing = true;
        },
        empty: function () {
            "use strict";
            var rp = rascal.picture;
            rp.showing = false;
            $('#' + rp.container).children().remove();
        }
    }
};
