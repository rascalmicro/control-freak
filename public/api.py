from flask import Blueprint, render_template, request

public = Blueprint('api', __name__, template_folder='templates')

### Support for pins ###
def toggle_pin(pin):
    if pytronics.digitalRead(pin) == '1':
        pytronics.digitalWrite(pin, 'LOW')
    else:
        pytronics.digitalWrite(pin, 'HIGH')

@public.route('/pin/<pin>/<state>')
def update_pin(pin, state):
    try:
        if state.lower() == 'on':
            pytronics.digitalWrite(pin, 'HIGH')
            return 'Set pin %s high' % pin
        elif state.lower() == 'off':                       
            pytronics.digitalWrite(pin, 'LOW')
            return 'Set pin %s low' % pin
        elif state.lower() == 'in':
            pytronics.pinMode(pin,'INPUT')
            return 'Set pin %s input' % pin
        elif state.lower() == 'out':
            pytronics.pinMode(pin,'OUTPUT')
            return 'Set pin %s output' % pin
        return "Something's wrong with your syntax. You should send something like: /pin/2/on"
    except:
        return 'Forbidden', 403

@public.route('/read-pins', methods=['POST'])
def read_pins():
    import json
    # return json.dumps(pytronics.readPins(LIVE_PINS))
    pins = pytronics.readPins(LIVE_PINS)
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
@public.route('/serial/<port>/<speed>/<message>', methods=['POST'])
def serial_write(port, speed, message):
    pytronics.serialWrite(message, speed, port)
    return 'Tried to write serial data.'

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
