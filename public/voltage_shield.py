import binascii, bitstring, pytronics, time
from flask import Blueprint, render_template, request

public = Blueprint('voltage_shield', __name__, template_folder='templates')

@public.route('/pvs/reset', methods=['GET', 'POST'])
def pvs_reset():
    pytronics.pinMode('4', 'OUTPUT')
    pytronics.digitalWrite('4', 'HIGH')
    pytronics.digitalWrite('4', 'LOW')
    return 'reset line pulsed high'

@public.route('/pvs/read', methods=['GET', 'POST'])
def pvs_read():
    pytronics.spiSetSpeed(1000000)
    pytronics.pinMode('3', 'INPUT')
    pytronics.pinMode('5', 'OUTPUT')
    pytronics.digitalWrite('5', 'LOW')
    pytronics.digitalWrite('5', 'HIGH')
    start = time.time()
    while((time.time() < start + 1000) and (pytronics.digitalRead('4') == '1')):
        pass
    data = pytronics.spiRead(14)
    b = bitstring.BitArray(hex=binascii.hexlify(data))
    return ', '.join([str(5*float(chunk.int)/16384) for chunk in b.cut(14)])