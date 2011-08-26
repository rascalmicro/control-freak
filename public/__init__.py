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
    import rascal
    pin = rascal.read_pin(2)
    (chan0, chan1, chan2, chan3) = rascal.summarize_analog_data()
    return render_template('/relay.html', chan0=chan0, chan1=chan1, chan2=chan2, chan3=chan3, pin=pin)

@public.route('/toggle', methods=['POST'])
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

@public.route('/lcd.html', methods=['POST'])
def write_serial():
    import rascal
    rascal.send_serial(request.form['serial_text'], 9600)
    return render_template('/lcd.html')

@public.route('/clear', methods=['POST'])
def clear_lcd():
    import rascal
    rascal.send_serial(chr(0xFE) + chr(0x01))
    return render_template('/lcd.html')
