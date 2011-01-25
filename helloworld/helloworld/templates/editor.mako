<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <script src="/codemirror/js/codemirror.js" type="text/javascript"></script>
    <title>CodeMirror: HTML mixed-mode demonstration</title>
    <link rel="stylesheet" type="text/css" href="/codemirror/css/docs.css"/>
  </head>
  <body style="padding: 20px;">

<p>
Test of the Rascal web-based code editor using <a href="http://codemirror.net">CodeMirror</a>. File loaded is <a href="${c.fileurl}">${c.sourcefile}</a>.
</p>

<form method="POST" action="/hello/save">
    <div style="border: 1px solid black; padding: 3px;">
        <textarea id="code" cols="120" rows="30" name="text">
<%include file="${c.sourcefile}" />
        </textarea>
    </div>
    <input type="submit" value="Save">
    <input type="hidden" name="fileurl" value="${c.fileurl}">
    <input type="hidden" name="sourcefile" value="${c.sourcefile}">
</form>

<script type="text/javascript">
  var editor = CodeMirror.fromTextArea('code', {
    height: "350px",
    parserfile: ["parsexml.js", "parsecss.js", "tokenizejavascript.js", "parsejavascript.js", "parsehtmlmixed.js"],
    stylesheet: ["/codemirror/css/xmlcolors.css", "/codemirror/css/jscolors.css", "/codemirror/css/csscolors.css"],
    path: "/codemirror/js/"
  });
</script>
  </body>
</html>
