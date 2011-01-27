<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Rascal demo</title>
    <link rel="stylesheet" type="text/css" href="http://fonts.googleapis.com/css?family=Droid+Sans|Molengo">
    <link rel="stylesheet" type="text/css" href="/style.css">
    <script src="http://code.jquery.com/jquery-1.4.4.js"></script>
    <script>
    function tellRascal() {
    $.ajax({
          type: "POST",
          url: "/hello/toggle",
          data: "target_state=" + $("#target_state").val(),
          success: function(resp){
          },
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
            <label for="target_state">Toggle relay</label>
            <select id="target_state" onchange="tellRascal();">
                % if c.pin == '1':
                <option value="0">Off</option>
                <option value="1" selected="selected">On</option>
                % else:
                <option value="0" selected="selected">Off</option>
                <option value="1">On</option>
                % endif
            </select>
            <p>Acknowledge the victory of your robot overlords.</p>
        </form>
        <form action="/hello/editor" method="POST">
            <input type="submit" value="edit this file">
            <input type="hidden" name="fileurl" value="/hello/index">
            <input type="hidden" name="sourcefile" value="index.mako">
        </form>
    </div>
</body>
</html>

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
