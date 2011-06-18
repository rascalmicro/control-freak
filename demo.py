import rascal
from flask import Flask, render_template, request, url_for
from werkzeug import secure_filename
app = Flask(__name__)

# Routes for editor #
# ----------------- #

@app.route('/edit')
def edit():
    return render_template('/editor.html', text_to_edit='No file selected')

@app.route('/get_dirlist', methods=['POST'])
def get_dirlist():
    try:
        import filetree
    except ImportError:
        print("Import error: can't find filetree")
    try:
        request.form['dir']
    except KeyError:
        print("Key error in attempt to list directory contents.")
    return str(filetree.dirlist(request.form['dir']))

@app.route('/new_file', methods=['POST'])
def new_file():
    import subprocess
    subprocess.Popen(['touch', '/var/www/editable/' + secure_filename(request.form['filename'])])
    return render_template('/editor.html', sourcefile=sourcefile)

@app.route('/new_folder', methods=['POST'])
def new_folder():
    import subprocess
    result = subprocess.Popen(['mkdir', '/var/www/editable/' + secure_filename(request.form['name'])])
    print result
    return render_template('/editor.html', sourcefile=sourcefile)

@app.route('/read_contents', methods=['POST'])
def read_contents():
    f = open('/var/www/editable/' + secure_filename(request.form['filepath']), 'r')
    return f.read()

@app.route('/reload', methods=['POST'])
def reload():
    import subprocess
    f = open('/etc/uwsgi.reload', 'w')
    f.write(request.form['text'])
    f.close()
    return render_template('/editor.html', sourcefile=sourcefile)

@app.route('/save', methods=['POST'])
def save():
    path = '/var/www/editable/'
    sourcefile = request.form['sourcefile']
    f = open(path + secure_filename(str(sourcefile)), 'w')
    f.write(request.form['text'])
    f.close()
    return render_template('/editor.html', sourcefile=sourcefile)

# Routes for demo pages #
# --------------------- #

@app.route('/lcd.html')
def lcd():
    return render_template('/lcd.html')

@app.route('/relay.html')
def index():
    pin = rascal.read_pin(2)
    (chan0, chan1, chan2, chan3) = rascal.summarize_analog_data()
    return render_template('/relay.html', chan0=chan0, chan1=chan1, chan2=chan2, chan3=chan3, pin=pin)

def toggle_relay():
    if (rascal.read_pin(2) == '1'):
        rascal.set_pin_low(2)
        return "low"
    else:
        rascal.set_pin_high(2)
    return "high"

@app.route('/toggle', methods=['POST'])
def toggle():
    if(request.form['target_state'] == '1'):
        rascal.set_pin_high(2)
        result = 'Pins set high'
    elif(request.form['target_state'] == '0'):
        rascal.set_pin_low(2)
        result = 'Pins set low'
    else:
        result = 'Target_state is screwed up'
    return result

@app.route('/lcd.html', methods=['POST'])
def write_serial():
    rascal.send_serial(request.form['serial_text'])
    return render_template('/lcd.html')

@app.route('/clear', methods=['POST'])
def clear_lcd():
    rascal.send_serial(chr(0xFE) + chr(0x01))
    return render_template('/lcd.html')

# Main app #
# -------- #

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
