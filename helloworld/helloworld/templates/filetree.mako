<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Rascal demo</title>

    <link rel="stylesheet" type="text/css" href="/jquery.filetree.css"/>
    <link rel="stylesheet" type="text/css" href="/codemirror/lib/codemirror.css"/>
    <link rel="stylesheet" type="text/css" href="/codemirror/mode/css/css.css"/>
    <link rel="stylesheet" type="text/css" href="/codemirror/mode/javascript/javascript.css"/>
    <link rel="stylesheet" type="text/css" href="/codemirror/mode/xml/xml.css"/>
    <link rel="stylesheet" type="text/css" href="/style.css">
    <link rel="stylesheet" type="text/css" href="http://fonts.googleapis.com/css?family=Droid+Sans|Molengo">

    <script type="text/javascript" src="/codemirror/lib/codemirror.js"></script>
    <script type="text/javascript" src="/codemirror/mode/css/css.js"></script>
    <script type="text/javascript" src="/codemirror/mode/htmlmixed/htmlmixed.js"></script>
    <script type="text/javascript" src="/codemirror/mode/javascript/javascript.js"></script>
    <script type="text/javascript" src="/codemirror/mode/xml/xml.js"></script>
    <script type="text/javascript" src="http://code.jquery.com/jquery-1.5.js"></script>
    <script type="text/javascript" src="/jquery.filetree.js"></script>
</head>
<body>
    <p>
    Test of the Rascal web-based code editor
    </p>

    <div id="ft-background">
        <div id="filetree"></div>
    </div>
    <div id="editor">
        <form method="POST" action="/hello/save">
            <input type="submit" value="Save">
            <div id="textfield">
        <%
                text_to_edit = 'No file selected'
                if(hasattr(c, 'sourcefile')):
                    path = '/home/root/helloworld/helloworld'
                    f = open(path + c.sourcefile, 'r')
                    text_to_edit = f.read()
                    f.close()
                else:
                    c.sourcefile = 'no-file-selected'
                    c.fileurl = 'no-file-url-yet'
        %>
                <textarea id="code" cols="100" rows="60" name="text">${text_to_edit}</textarea>
            </div>
            <input id="fileurl" type="hidden" name="fileurl" value="${c.fileurl}">
            <input id="sourcefile" type="hidden" name="sourcefile" value="${c.sourcefile}">
        </form>
    </div>
    <script type="text/javascript">
    var editor = CodeMirror.fromTextArea(document.getElementById('code'), {
        mode: "text", // text mode doesn't exist explicitly, but setting it provokes plain text by default
        tabMode: "shift",
        indentUnit: "4",
        enterMode: "keep",
        electricChars: false
    });

    function pickMode(ext) {
        switch(ext.toLowerCase()) {
            case "css":
                return "css";
            case "js":
                return "javascript";
            case "py":
                return "python";
            default:
                return "htmlmixed";
        }    
    }

    function openFile(path) {
        $.get('read_contents', {filepath: path}, function(result) {
            editor.setValue(result);
            a = path.split(".");
            ext = a[a.length - 1];
            editor.setOption('mode', pickMode(ext));
            $('#fileurl').val(path);
            $('#sourcefile').val(path);
        }); 
    };

    $(document).ready( function() {
        $('#filetree').fileTree({ root: '/home/root/helloworld/helloworld', script: '/hello/get_dirlist' }, function(path) { 
            openFile(path.split('/home/root/helloworld/helloworld')[1]);
        });
    });
    </script>
</body>
</html>
