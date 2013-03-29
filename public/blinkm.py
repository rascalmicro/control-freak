import colorsys, json, pytronics
from flask import Blueprint, render_template, request

public = Blueprint('blinkm', __name__, template_folder='templates')

@public.route('/blinkm/hsb/<address>/<hue>/<saturation>/<brightness>', methods=['GET', 'POST'])
def blinkm_set_hsb(address, hue, saturation, brightness):
    import subprocess
    cmd = ('blinkm fade-hsb -d ' + address +
           ' -h ' + hue +
           ' -s ' + saturation +
           ' -b ' + brightness)
    print cmd
    subprocess.Popen([cmd], shell=True)
    return 'HSB triplet ({0}, {1}, {2}) sent to Blinkm at address {3}'.format(hue, saturation, brightness, address)

@public.route('/blinkm/hsb/<address>', methods=['GET', 'POST'])
def blinkm_get_hsb(address):
    rgb = pytronics.i2cRead(int(address), 0x67, 'I', 3)
    return json.dumps(zip(['hue', 'saturation', 'brightness'], colorsys.rgb_to_hsv(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)))

@public.route('/blinkm/rgb/<address>/<red>/<green>/<blue>', methods=['GET', 'POST'])
def blinkm_set_rgb(address, red, green, blue):
    import subprocess
    cmd = ('blinkm fade-rgb -d ' + address +
           ' -r ' + red +
           ' -g ' + green +
           ' -b ' + blue)
    print cmd
    subprocess.Popen([cmd], shell=True)
    return 'RGB triplet ({0}, {1}, {2}) sent to Blinkm at address {3}'.format(red, green, blue, address)

@public.route('/blinkm/rgb/<address>', methods=['GET', 'POST'])
def blinkm_get_rgb(address):
    rgb = pytronics.i2cRead(int(address), 0x67, 'I', 3)
    return json.dumps(zip(['red', 'green', 'blue'], rgb))