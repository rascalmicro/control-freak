import colorsys, json, pytronics
from flask import Blueprint, render_template, request

public = Blueprint('blinkm', __name__, template_folder='templates')

@public.route('/blinkm/<address>/hsb/<hue>/<saturation>/<brightness>', methods=['GET', 'POST'])
def blinkm_set_hsb(address, hue, saturation, brightness):
    import subprocess
    cmd = ('blinkm fade-hsb -d ' + address +
           ' -h ' + hue +
           ' -s ' + saturation +
           ' -b ' + brightness +
           '; blinkm stop-script -d ' + address)
    print cmd
    subprocess.Popen([cmd], shell=True)
    return ('HSB sent to Blinkm')

@public.route('/blinkm/<address>/hsb', methods=['GET', 'POST'])
def blinkm_get_hsb(address):
    rgb = pytronics.i2cRead(int(address), 0x67, 'I', 3)
    return json.dumps(zip(['hue', 'saturation', 'brightness'], colorsys.rgb_to_hsv(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)))