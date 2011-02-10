<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Rascal demo</title>
    <link rel="stylesheet" type="text/css" href="http://fonts.googleapis.com/css?family=Droid+Sans|Molengo">
    <link rel="stylesheet" type="text/css" href="/style.css">
    <script src="http://code.jquery.com/jquery-1.5.js"></script>
    <!--[if IE]><script language="javascript" type="text/javascript" src="/excanvas.js"></script><![endif]-->
    <script language="javascript" type="text/javascript" src="/jquery.jqplot.js"></script>
    <link rel="stylesheet" type="text/css" href="/jquery.jqplot.css" />
    <script language="javascript" type="text/javascript">
    function tellRascal() {
        $.ajax({
            type: "POST",
            url: "/hello/toggle",
            data: "target_state=" + $("#target_state").val(),
            success: function(resp){},
            error: function(e){
                alert('Error: ' + e);
            }
        });
    }
    </script>
</head>
<body>
    <div class="rascalcontent">
        <h1>Rascal demo</h1>
        <form id="relay-form">
            <label for="target_state">Toggle relay on Brandon's desk:</label>
            <select id="target_state" onchange="tellRascal();">
                % if c.pin == '1':
                <option value="0">Off</option>
                <option value="1" selected="selected">On</option>
                % else:
                <option value="0" selected="selected">Off</option>
                <option value="1">On</option>
                % endif
            </select>
            <p>Mubarak must go!</p>
        </form>
        <div id="chart1" style="height:300px;width:700px;"></div>
        <form id="serial_form" action="/hello/write_serial" method="POST" style="margin-left:87px">
            <label for="serial_text">Text to send to LCD display on Brandon's desk</label>
            <input id="serial_text" name="serial_text" type="textarea" style="height:100px;width:600px;border:0px">
            <input type="submit" value="Send text">
        </form>
        <hr />
        <form action="/hello/editor" method="POST">
            <input type="submit" value="edit this file">
            <input type="hidden" name="fileurl" value="/hello/index">
            <input type="hidden" name="sourcefile" value="index.mako">
        </form>
    </div>
    <script language="javascript" type="text/javascript">
    $.jqplot("chart1",[[[1, 2],[3,5.12],[5,13.1],[7,33.6],[9,85.9],[11,73],[9,65],[8.5,90]]], {
        axes: {
            xaxis: {
                label: 'time' },
            yaxis: {
                label: 'sensor' } 
        }
    });
    </script>
</body>
</html>