<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Rascal demo</title>
    <link rel="stylesheet" type="text/css" href="/jquery.filetree.css"/>
    <link rel="stylesheet" type="text/css" href="/style.css">
    <script src="http://code.jquery.com/jquery-1.5.js"></script>
    <script language="javascript" type="text/javascript" src="/jquery.filetree.js"></script>
</head>
<body style="padding: 20px;">
    <script language="javascript" type="text/javascript"> 
    $(document).ready( function() {
        $('#filetree').fileTree({ root: '/home/root/helloworld', script: '/hello/get_dirlist' }, function(file) { 
            alert(file);
        });
    });
    </script>
    <p>
    Test of the filetree
    </p>
    <div id="filetree"></div>

</body>
</html>
