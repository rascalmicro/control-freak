import pytronics, webcolors
from math import pi, radians, sin

def clear_lcd(): # also moves cursor to 0,0
    pytronics.serialWrite(chr(0xFF) + chr(0xCD), 9600)

def put_string(data):
    pytronics.serialWrite(chr(0x00) + chr(0x18) + data + chr(0x00), 9600)

def draw_filled_rectangle(x1, y1, x2, y2, color):
    # limit to x to 480, y to 272
    try:
        if int(color,16):
            hex_color = webcolors.hex_to_rgb('#' + color)
        elif color == '000000':
            hex_color = (0, 0, 0)
    except ValueError:
        hex_color = webcolors.name_to_rgb(color)
    upper_color_byte = (hex_color[0] >> 3 << 3) + (hex_color[1] >> 5) # RRRRR GGG
    lower_color_byte = (hex_color[1] >> 2 << 5) % 256 + (hex_color[2] >> 3) # GGG BBBBB
    #print bin(upper_color_byte), bin(lower_color_byte)
    pytronics.serialWrite(chr(0xFF) + chr(0xC4) + chr(x1/256) + chr(x1%256) + chr(y1/256) + chr(y1%256)+ chr(x2/256) + chr(x2%256)+ chr(y2/256) + chr(y2%256) + chr(upper_color_byte) + chr(lower_color_byte), 9600)

def draw_sinusoidal_grating(period):
    for col in range(480):
        color = int(127.5 * (1 + sin(col * 2 * pi / period)))
        draw_filled_rectangle(col, 0, col, 272, '{0:06x}'.format(color))
        