from flask import Blueprint, render_template, request
from pytronics import serialWrite
public = Blueprint('libservo', __name__, template_folder='templates')

POLOLU_PROTOCOL = chr(0xAA)
SET_TARGET = chr(0x04)
SERVO_ZERO_TIME = 6000

@public.route('/pmservo/<channel>/<speed>', methods=['GET', 'POST'])
def set_target_speed(channel, speed):
    ispeed = max(min(int(speed), 200), -200)
    lsb = ispeed + SERVO_ZERO_TIME & 0x7F
    msb = (ispeed + SERVO_ZERO_TIME >> 7) & 0x7F
    
    data = bytearray()
    data += POLOLU_PROTOCOL
    data += chr(0x0C)
    data += SET_TARGET
    if int(channel) == 1:
        data += chr(0x01)
    else:
        data += chr(0x02)
    data += chr(lsb)
    data += chr(msb)
    serialWrite(data)
    return 'Sent data to servo controller: LSB: {0}, MSB: {1}'.format(lsb, msb)