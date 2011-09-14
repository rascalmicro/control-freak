from flask import Blueprint, render_template, request

public = Blueprint('public', __name__, static_folder='static', template_folder='templates')

@public.route('/arduino.html')
def arduino():
    return render_template('/arduino.html')

@public.route('/lcd.html')
def lcd():
    return render_template('/lcd.html')

@public.route('/relay.html')
def index():
    import pytronics
    pin = pytronics.read_pin(2)
    (chan0, chan1, chan2, chan3) = pytronics.summarize_analog_data()
    return render_template('/relay.html', chan0=chan0, chan1=chan1, chan2=chan2, chan3=chan3, pin=pin)

@public.route('/toggle', methods=['POST'])
def toggle():
    import pytronics
    if(request.form['target_state'] == '1'):
        pytronics.set_pin_high(2)
        result = 'Pins set high'
    elif(request.form['target_state'] == '0'):
        pytronics.set_pin_low(2)
        result = 'Pins set low'
    else:
        result = 'Target_state is screwed up'
    return result

@public.route('/analog', methods=['POST'])
def analog():
    from pytronics import read_analog
    import json, time
    data = {
        "time" : float(time.time()),
        "A0" : float(read_analog('A0')) * 3.3 / 1024.0,
        "A1" : float(read_analog('A1')) * 3.3 / 1024.0,
        "A2" : float(read_analog('A2')) * 3.3 / 1024.0,
        "A3" : float(read_analog('A3')) * 3.3 / 1024.0
    }
    return json.dumps(data)

@public.route('/lcd.html', methods=['POST'])
def write_serial():
    import pytronics
    pytronics.send_serial(request.form['serial_text'], 9600)
    return render_template('/lcd.html')

@public.route('/clear', methods=['POST'])
def clear_lcd():
    import pytronics
    pytronics.send_serial(chr(0xFE) + chr(0x01), 9600)
    return render_template('/lcd.html')
