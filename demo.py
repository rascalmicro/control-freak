import rascal
from flask import Flask, render_template, request, url_for
app = Flask(__name__)

def filetree(self):
    return render_template('/filetree.html')

def get_dirlist(self):
    import filetree
    return filetree.dirlist(request)

def read_contents(self):
    f = open('/home/root/helloworld/helloworld' + request.params['filepath'], 'r')
    return f.read()

@app.route('/lcd.html')
def lcd():
    return render_template('/lcd.html')

@app.route('/relay.html')
def index():
    pin = rascal.read_pin(66)
    (chan0, chan1, chan2, chan3) = rascal.summarize_analog_data() 
    return render_template('/relay.html', chan0=chan0, chan1=chan1, chan2=chan2, chan3=chan3, pin=pin)

def save(self):
    path = '/home/root/helloworld/helloworld/'
    c.fileurl = request.params['fileurl']
    c.sourcefile = request.params['sourcefile']
    f = open(path + str(c.sourcefile), 'w')
    f.write(request.params['text'])
    f.close()
    return render_template('/filetree.html')

@app.route('/toggle-relay')
def toggle_relay():
    if (rascal.read_pin(71) == '1'):
        rascal.set_pin_low(71)
        return "low"
    else:
        rascal.set_pin_high(71)
    return "high"

@app.route('/toggle', methods=['POST'])
def toggle():
    if(request.form['target_state'] == '1'):
        rascal.set_pin_high(66)
        rascal.set_pin_high(71)
        result = 'Pins set high'
    elif(request.form['target_state'] == '0'):
        rascal.set_pin_low(66)
        rascal.set_pin_low(71)
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
