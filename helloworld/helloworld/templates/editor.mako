<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <script src="/codemirror/js/codemirror.js" type="text/javascript"></script>
    <title>Rascal demo</title>
    <link rel="stylesheet" type="text/css" href="/codemirror/css/docs.css"/>
    <link rel="stylesheet" type="text/css" href="/style.css">
  </head>
  <body style="padding: 20px;">

<p>
Test of the Rascal web-based code editor using <a href="http://codemirror.net">CodeMirror</a>. File loaded is <a href="${c.fileurl}">${c.sourcefile}</a>.
</p>

<form method="POST" action="/hello/save">
    <input type="submit" value="Save">
    <div style="border: 1px solid black; padding: 3px;">
<%
    path = '/home/root/helloworld/helloworld/templates/'
    f = open(path + c.sourcefile, 'r')
    text_to_edit = f.read()
    f.close()
%>
        <textarea id="code" cols="120" rows="30" name="text">${text_to_edit}</textarea>
    </div>
    <input type="hidden" name="fileurl" value="${c.fileurl}">
    <input type="hidden" name="sourcefile" value="${c.sourcefile}">
</form>

<script type="text/javascript">
  var editor = CodeMirror.fromTextArea('code', {
    height: "600px",
    parserfile: ["parsexml.js", "parsecss.js", "tokenizejavascript.js", "parsejavascript.js", "parsehtmlmixed.js"],
    stylesheet: ["/codemirror/css/xmlcolors.css", "/codemirror/css/jscolors.css", "/codemirror/css/csscolors.css"],
    path: "/codemirror/js/"
  });
</script>
  </body>
</html>
