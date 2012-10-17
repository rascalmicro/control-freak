from flask import Flask, render_template, request
from uwsgidecorators import *
import pytronics
import os, time

public = Flask(__name__)
public.config['PROPAGATE_EXCEPTIONS'] = True

# Include "no-cache" header in all POST responses
@public.after_request
def add_no_cache(response):
    if request.method == 'POST':
        response.cache_control.no_cache = True
    return response

# config for upload
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
ALLOWED_DIRECTORIES = set(['static/uploads/', 'static/pictures/'])
LIVE_PINS = ['LED', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13']
# public.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

### Home page ###
@public.route('/')
@public.route('/index.html')
def default_page():
    try:
        with open('/etc/hostname', 'r') as f:
            name = f.read().strip().capitalize()
    except:
        name = 'Rascal'
    return render_template('/index.html', hostname=name, template_list=get_public_templates())

def get_public_templates():
    r = []
    d = '/var/www/public/templates'
    for f in os.listdir(d):
        ff=os.path.join(d,f)
        if os.path.isfile(ff):
            r.append(f)
    return sorted(r)

# Format date/time in Jinja template
@public.template_filter()
def datetimeformat(value, format='%H:%M / %d-%m-%Y'):
    return time.strftime(format, value)

# Return current date and time in specified format
@public.route('/datetime', methods=['POST'])
def datetime():
    try:
        format = request.form['format']
    except:
        format = '%d %b %Y %H:%M %Z'
    return time.strftime(format, time.localtime())

### Generic HTML and Markdown templates, support for doc tab ###
@public.route('/<template_name>.html')
def template(template_name):
    return render_template(template_name + '.html', magic="Hey presto!")

@public.route('/<doc_name>.md')
def document(doc_name):
    return render_markdown('', doc_name)

@public.route('/docs/<doc_name>.md')
def document_docs(doc_name):
    return render_markdown('docs/', doc_name)

def render_markdown(path, doc_name):
    import markdown2
    with open('/var/www/public/templates/' + path + doc_name + '.md', 'r') as mdf:
        return render_template('documentation.html', title=doc_name, markdown=markdown2.markdown(mdf.read()))
    return 'Not Found', 404

@public.route('/get_markdown', methods=['POST'])
def get_markdown():
    import markdown2
    doc_name = request.form['docName']
    try:
        with open('/var/www/public/templates/docs/' + doc_name + '.md', 'r') as mdf:
            return markdown2.markdown(mdf.read())
    except:
        try:
            with open('/var/www/public/templates/' + doc_name + '.md', 'r') as mdf:
                return markdown2.markdown(mdf.read())
        except:
            with open('/var/www/public/templates/docs/default.md', 'r') as mdf:
                return markdown2.markdown(mdf.read())
    return 'Internal server error', 500

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

### Specific demos ###
# analog-graph
@public.route('/analog', methods=['POST'])
def analog():
    import json
    try:
        ad_ref = float(request.form['adref'])
    except KeyError:
        ad_ref = 3.3
    data = {
        "time" : float(time.time()),
        "A0" : float(pytronics.analogRead('A0')) * ad_ref / 1024.0
    }
    return json.dumps(data)

# relay (also calls analog)
@public.route('/relay.html')
def index():
    pin = pytronics.digitalRead(2)
    (chan0, chan1, chan2, chan3) = [pytronics.analogRead(chan) for chan in ['A0', 'A1', 'A2', 'A3']]
    return render_template('/relay.html', chan0=chan0, chan1=chan1, chan2=chan2, chan3=chan3, pin=pin)

@public.route('/toggle', methods=['POST'])
def toggle():
    if(request.form['target_state'] == '1'):
        pytronics.digitalWrite(2, 'HIGH')
        result = 'Pins set high'
    elif(request.form['target_state'] == '0'):
        pytronics.digitalWrite(2, 'LOW')
        result = 'Pins set low'
    else:
        result = 'Target_state is screwed up'
    return result

# thermostat
#@rbtimer(60)
@public.route('/temperature', methods=['POST'])
def temperature():
    import json, thermostat
    f = open('/var/www/public/thermostat-target.txt', 'r')
    data = {
        "time" : float(time.time()),
        "actual" : float(thermostat.read_sensor(0x48)),
        "target" : float(f.read())
        #"target" : thermostat.get_target_temp('/var/www/public/static/basic.ics', 'America/New_York')
    }
    return json.dumps(data)

def fetch_calendar(num):
    import thermostat
    thermostat.update_calendar_file()
    print('Calendar reload attempt')

#@rbtimer(3)
def update_relay(num):
    import thermostat
    actual = float(thermostat.read_sensor(0x48)) * 1.8 + 32.0
    target = float(thermostat.get_target_temp('/var/www/public/static/basic.ics', 'America/New_York'))
    print("Measured temperature: %f degrees. Target is %f degrees." % (actual, target))
    if actual < target:
        pytronics.digitalWrite(2, 'HIGH')
        print("Heat on")
    else:
        pytronics.digitalWrite(2, 'LOW')
        print("Heat off")

@public.route('/sms', methods=['POST'])
def parse_sms():
    import subprocess
    message = request.form['Body']
    print "Received text message: " + str(message)
    f = open('/var/www/public/thermostat-target.txt', 'w')
    f.write(str(message))
    f.close()
    return ('Message processed')

# lcd (serial)
@public.route('/send-to-lcd', methods=['POST'])
def send_to_lcd():
    pytronics.serialWrite(request.form['serial_text'], 9600)
    return render_template('/lcd.html')

@public.route('/clear-lcd', methods=['POST'])
def clear_lcd():
    pytronics.serialWrite(chr(0xFE) + chr(0x01), 9600)
    return render_template('/lcd.html')

# ck (Color Kinetics)
@public.route('/set-color', methods=['POST'])
def set_color():
    import colorsys, kinet, subprocess
    color = request.form['color']
    print "RGB = " + str(color)
    pds = kinet.PowerSupply("192.168.10.57")
    pds.append(kinet.FixtureRGB(0))
    hsv = (colorsys.rgb_to_hsv(int(color[0:2], 16)/255.0, int(color[2:4], 16)/255.0, int(color[4:6], 16)/255.0))
    print "HSV = " + str(hsv)
    pds[0].hsv = hsv
    pds.go()
    return ('color sent to Color Kinetics box')

# BlinkM smart LED
@public.route('/set-blinkm', methods=['POST'])
def set_blinkm():
    import subprocess
    color = request.form['color']
    cmd = ('blinkm set-rgb -d 9' +
           ' -r ' + str(int(color[0:2], 16)) +
           ' -g ' + str(int(color[2:4], 16)) +
           ' -b ' + str(int(color[4:6], 16)) +
           '; blinkm stop-script -d 9')
    print cmd
    subprocess.Popen([cmd], shell=True)
    return ('Color sent to Blinkm')

# sprinkler
@public.route('/sprinkler', methods=['POST'])
def sprinkler():
    command = request.form['command']
    if(command == "ON"):
        pytronics.digitalWrite(2, 'HIGH')
    else:
        pytronics.digitalWrite(2, 'LOW')
    return ('Sprinkler toggled')
### End of specific demo procedures

### The following procedures support sending email via SMTP ###
# They are used by email.html. Configure smtp settings in smtp_lib.py
@public.route('/')
@public.route('/email.html')
def email_form():
    import smtp_lib
    return render_template('email.html', sender=smtp_lib.sender(), help=smtp_lib.help())

@public.route('/send-email', methods=['POST'])
def send_email():
    import smtp_lib, json
    sender = request.form['sender'].strip()
    recipients = request.form['recipients'].strip()
    subject = request.form['subject'].strip()
    body = request.form['body'].strip()
    if sender == '':
        result = (1, 'Please enter the sender')
    elif recipients == '':
        result = (1, 'Please enter at least one recipient')
    else:
        result = smtp_lib.sendmail(sender, recipients, subject, body)
    data = {
        "status" : int(result[0]),
        "message" : result[1]
    }
    return json.dumps(data)
### End of email procedures

### The following procedures support file upload ###
# They are called from rascal-1.03.js and used by upload-cf.html, upload-dd.html and album.html
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_folder(folder):
    return folder in ALLOWED_DIRECTORIES

@public.route('/xupload', methods=['POST'])
def xupload_file():
    import os
    from werkzeug import secure_filename
    from werkzeug.exceptions import RequestEntityTooLarge
    if request.method == 'POST':
        try:
            root = '/var/www/public/'
            # Check file type and folder
            filename = secure_filename(request.headers['X-File-Name'])
            if not allowed_file(filename):
                print '## xupload ## bad file type ' + filename
                return 'Forbidden', 403
            try:
                folder = request.headers['X-Folder']
            except:
                folder = ''
            if not allowed_folder(folder):
                print '## xupload ## bad folder ' + folder
                return 'Forbidden', 403
            fpath = os.path.join(root, os.path.join(folder, filename))
            # Write out the stream
            f = file(fpath, 'wb')
            f.write(request.stream.read())
            f.close()
            print '## xupload ## ' + fpath
        except RequestEntityTooLarge:
            return 'File too large', 413
        except:
            return 'Bad request', 400
    return 'OK', 200

@public.route('/list-directory', methods=['POST'])
def list_directory():
    import os, json
    root = '/var/www/public/'
    dir = request.form['directory']
    try:
        dirlist = os.listdir(os.path.join(root, dir))
        return json.JSONEncoder().encode(dirlist)
    except OSError:
        return 'Not Found', 404
    except Exception, e:
        print '## list_directory ## {0}'.format(e)
    return 'Bad request', 400

@public.route('/clear-directory', methods=['POST'])
def clear_directory():
    import os
    root = '/var/www/public/'
    dir = request.form['directory']
    if dir not in ALLOWED_DIRECTORIES:
        return 'Forbidden', 403
    folder = os.path.join(root, dir)
    try:
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception, e:
                print '## clear_directory ## {0}'.format(e)
                return 'Bad request', 400
        return 'OK', 200
    except OSError:
        return 'Not Found', 404
    except Exception, e:
        print '## clear_directory ## {0}'.format(e)
    return 'Bad request', 400
### End of upload procedures ###

# Called from hello.html
@public.route('/flash_led', methods=['POST'])
def flash_led():
    if pytronics.digitalRead('LED') == '1':
        pytronics.digitalWrite('LED', 'LOW')
        message = "LED off"
    else:
        pytronics.digitalWrite('LED', 'HIGH')
        message = "LED on"
    return (message)


if __name__ == "__main__":
    public.run(host='127.0.0.1:5000', debug=True)
