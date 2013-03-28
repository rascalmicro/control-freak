from flask import Blueprint, render_template, request
import pytronics

public = Blueprint('api', __name__, template_folder='templates')

ANALOG_PINS = ['A0', 'A1', 'A2', 'A3']
DIGITAL_PINS = ['LED', '2', '3', '4', '5', '6', '7']
DIGITAL_PIN_NAME_ERROR = "You seem to be trying to read from digital pin {0}, which does not work. Try 'LED', '2', '3', '4', '5', '6', or '7'."
DIGITAL_PIN_STATE_ERROR = "You seem to be trying to set digital pin {0} to state {1}, which does not work. Try 'LOW' or 'HIGH'."

### Support for pins ###

@public.route('/analog/read/<pin_name>', methods=['GET', 'POST'])
def analog_read(pin_name):
    if pin_name not in ANALOG_PINS:
        return "You seem to be trying to read from analog pin {0}, which does not exist. Try A0, A1, A2, or A3.".format(pin_name)
    else:
        return pytronics.analogRead(pin_name)

@public.route('/digital/read/<pin_name>', methods=['GET', 'POST'])
def digital_read(pin_name):
    if pin_name not in DIGITAL_PINS:
        return DIGITAL_PIN_NAME_ERROR.format(pin_name)
    else:
        return pytronics.digitalRead(pin_name)

@public.route('/digital/write/<pin_name>', methods=['GET', 'POST'])
def digital_write(pin_name):
    if pin_name in DIGITAL_PINS:
        data = request.form['data'].upper()
        if data in ['1', 'ON', 'HIGH']:
            pytronics.digitalWrite(pin_name, 'HIGH')
            return 'Set pin {0} to HIGH'.format(pin_name)
        elif data in ['0', 'OFF', 'LOW']:
            pytronics.digitalWrite(pin_name, 'LOW')
            return 'Set pin {0} to LOW'.format(pin_name)
        else:
            return DIGITAL_PIN_STATE_ERROR.format(pin_name, data)
    else:
        return DIGITAL_PIN_NAME_ERROR.format(pin_name)
    
@public.route('/digital/toggle/<pin_name>', methods=['GET', 'POST'])
def digital_toggle(pin_name):
    if pin_name in DIGITAL_PINS:
        if pytronics.digitalRead(pin_name) == '1':
            pytronics.digitalWrite(pin_name, 'LOW')
            return 'Set pin {0} to LOW'.format(pin_name)
        else:
            pytronics.digitalWrite(pin_name, 'HIGH')
            return 'Set pin {0} to HIGH'.format(pin_name)
    else:
        return DIGITAL_PIN_NAME_ERROR.format(pin_name)

@public.route('/digital/write/<pin_name>/<state>')
def digital_write_shortcut(pin_name, state):
    if pin_name in DIGITAL_PINS:
        if state.upper() in ['1', 'ON', 'HIGH']:
            pytronics.digitalWrite(pin_name, 'HIGH')
            return 'Set pin {0} to HIGH'.format(pin_name)
        elif state.upper() in ['0', 'OFF', 'LOW']:                       
            pytronics.digitalWrite(pin_name, 'LOW')
            return 'Set pin {0} to LOW'.format(pin_name)
        else:
            return DIGITAL_PIN_STATE_ERROR.format(pin_name, data)
    else:
        return DIGITAL_PIN_NAME_ERROR.format(pin_name)

@public.route('/read-pins', methods=['POST'])
def read_pins():
    import json
    # return json.dumps(pytronics.readPins(DIGITAL_PINS))
    pins = pytronics.readPins(DIGITAL_PINS)
    analog = {}
    for chan in ['A0', 'A1', 'A2', 'A3']:
        analog[chan] = pytronics.analogRead(chan)
    return json.dumps({ 'pins': pins, 'analog': analog })
        
### Support for i2c ###
@public.route('/i2cget/<addr>/<reg>/<mode>')
def i2cget(addr, reg, mode):
    iaddr = int(addr, 0)
    ireg = int(reg, 0)
    try:
        res = pytronics.i2cRead(iaddr, ireg, mode)
        print '## i2cget ## {0}'.format(res)
        return str(res)
    except (OSError, IOError) as e:
        import errno
        print '## i2cget ## Error: [{0}] {1}'.format(errno.errorcode[e.errno], e.strerror)
        return str(-1)
    except Exception as e:
        return 'Internal server error', 500

@public.route('/i2cset/<addr>/<reg>/<val>/<mode>')
def i2cset(addr, reg, val, mode):
    iaddr = int(addr, 0)
    ireg = int(reg, 0)
    ival = int(val, 0)
    try:
        pytronics.i2cWrite(iaddr, ireg, ival, mode)
        print '## i2cset ##'
        return str(0)
    except (OSError, IOError) as e:
        import errno
        print '## i2cset ## Error: [{0}] {1}'.format(errno.errorcode[e.errno], e.strerror)
        return str(-1)
    except Exception as e:
        return 'Internal server error', 500

@public.route('/i2c_read', methods=['POST'])
def i2c_read():
    import json
    try:
        params = json.loads(request.form['params'])
        print '## i2c_read ## ' + str(params)
        value = pytronics.i2cRead(params['addr'], params['reg'], params['size'], params['length'])
        result = {
            'success': True,
            'value': value
        }
        return json.dumps(result)
    except (OSError, IOError) as e:
        import errno
        print '## i2c_read ## Error: [{0}] {1}'.format(errno.errorcode[e.errno], e.strerror)
        result = {
            'success': False,
            'errorCode': errno.errorcode[e.errno],
            'errorMessage': e.strerror
        }
        return json.dumps(result)
    except Exception as e:
        return 'Internal server error', 500

@public.route('/i2c_write', methods=['POST'])
def i2c_write():
    import json
    try:
        params = json.loads(request.form['params'])
        print '## i2c_write ## ' + str(params)
        pytronics.i2cWrite(params['addr'], params['reg'], params['value'], params['size'])
        result = {
            'success': True
        }
        return json.dumps(result)
    except (OSError, IOError) as e:
        import errno
        print '## i2c_write ## Error: [{0}] {1}'.format(errno.errorcode[e.errno], e.strerror)
        result = {
            'success': False,
            'errorCode': errno.errorcode[e.errno],
            'errorMessage': e.strerror
        }
        return json.dumps(result)
    except Exception as e:
        return 'Internal server error', 500

@public.route('/i2cscan', methods=['POST'])
def i2cscan():
    from i2c import scanBus
    import json
    return json.dumps(scanBus())

### Support for serial ###
@public.route('/serial/read/<channel>/<speed>/<num_bytes>', methods=['GET', 'POST'])
def serial_read(channel, speed, num_bytes):
    return 'Fake data' # pytronics.serialRead(num_bytes, speed, channel)

@public.route('/serial/write/<channel>/<speed>', methods=['GET', 'POST'])
def serial_write(channel, speed):
    data = request.form['data']
    pytronics.serialWrite(data, speed, channel)
    return 'Sent to serial port {0} at {1} bps: {2}'.format(channel, speed, data)

### Support for SPI bus ###
@public.route('/spi/<channel>/read')
def spi_read(channel):
    if str(channel) not in ['0', '1', '2', '3']:
        return "You seem to be trying to read from SPI channel {0}, which does not exist. Try 0, 1, 2, or 3.".format(channel)
    return pytronics.spiRead(channel)

@public.route('/spi/<channel>/write/<data>')
def spi_write():
    if str(channel) not in ['0', '1', '2', '3']:
        return "You seem to be trying to write to SPI channel {0}, which does not exist. Try 0, 1, 2, or 3.".format(channel)
    return pytronics.spiWrite(data, channel)

@public.route('/spi/<channel>/speed/', defaults={'target': ''})
@public.route('/spi/<channel>/speed/<target>')
def spi_speed(channel, target):
    if str(channel) not in ['0', '1', '2', '3']:
        return "You seem to be trying to use SPI channel {0}, which does not exist. Try 0, 1, 2, or 3.".format(channel)
    if str(target) == '':
        return str(pytronics.spiGetSpeed(str(channel)))
    return str(pytronics.spiSetSpeed(target, channel))
