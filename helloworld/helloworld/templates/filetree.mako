<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Rascal demo</title>
    <link rel="stylesheet" type="text/css" href="/jquery.filetree.css"/>
    <link rel="stylesheet" type="text/css" href="/codemirror/css/docs.css"/>
    <link rel="stylesheet" type="text/css" href="/style.css">
    <script src="/codemirror/js/codemirror.js" type="text/javascript"></script>
    <script src="http://code.jquery.com/jquery-1.5.js"></script>
    <script language="javascript" type="text/javascript" src="/jquery.filetree.js"></script>
</head>
<body style="padding: 20px;">
    <script language="javascript" type="text/javascript"> 
    </script>
    <p>
    Test of the filetree
    </p>
    <div id="filetree"></div>

    <p>
    Test of the Rascal web-based code editor using <a href="http://codemirror.net">CodeMirror</a>.
    </p>

    <form method="POST" action="/hello/save">
        <input type="submit" value="Save">
        <div style="border: 1px solid black; padding: 3px;">
    <%
            text_to_edit = 'No file selected'
            if(hasattr(c, 'sourcefile')): 
                path = '/home/root/helloworld/helloworld/templates/'
                f = open(path + c.sourcefile, 'r')
                text_to_edit = f.read()
                f.close()
    %>
            <textarea id="code" cols="120" rows="30" name="text">${text_to_edit}</textarea>
        </div>
    </form>

    <script type="text/javascript">
    var editor = CodeMirror.fromTextArea('code', {
        height: "600px",
        parserfile: ["parsexml.js", "parsecss.js", "tokenizejavascript.js", "parsejavascript.js", "parsehtmlmixed.js"],
        stylesheet: ["/codemirror/css/xmlcolors.css", "/codemirror/css/jscolors.css", "/codemirror/css/csscolors.css"],
        path: "/codemirror/js/",
        tabMode: "spaces",
        indentUnit: "4",
        enterMode: "keep",
        electricChars: false
    });

    function openFile(path) {
        $.get(path, function(result) {
            editor.setCode(result);
        });
    };

    $(document).ready( function() {
        $('#filetree').fileTree({ root: '/home/root/helloworld/helloworld/public', script: '/hello/get_dirlist' }, function(path) { 
            openFile(path);
        });
    });
    </script>
</body>
</html>
