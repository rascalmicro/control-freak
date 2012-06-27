# Tmp file for prototyping changes to Pytronics

# Listing of /sys/class/gpio
# export      gpio107     gpio66      gpio69      gpio72      gpio97      gpiochip32  unexport
# gpio100     gpio64      gpio67      gpio70      gpio73      gpio98      gpiochip64

def decode_pin_name(pin):
    names = {
        'LED': 107, # PC11
        '0': 69, # PB5
        '1': 68, # PB4
        '2': 71, # PB7
        '3': 70, # PB6
        '4': 73, # PB9
        '5': 72, # PB8
        '6': 55, # PA23
        '7': 56, # PA24
        '8': 100, # PC4
        '9': 101, # PC5
        '10': 67, # PB3
        '11': 65, # PB1
        '12': 64, # PB0
        '13': 66, # PB2
        'A0': 96, # PC0
        'A1': 97, # PC1
        'A2': 98, # PC2
        'A3': 99, # PC3
    }
    try:
        return names[str(pin)]
    except KeyError as bad_name:
        print("There's no pin called {0}. Try a pin 3-13, 'LED', or 'A0'-'A3'.".format(bad_name)) 

# Write a HIGH or LOW value to a digital pin
# E.g. digitalWrite('11', 'HIGH')
def digitalWrite(pin, state):
    pin = decode_pin_name(pin)
    with open('/sys/class/gpio/gpio' + str(pin) + '/value', 'w') as f:
        if (state == 'HIGH'):
            f.write('1')
        else:
            f.write('0')

# Reads a value from a specified digital pin
# Returns '0' or '1'
def digitalRead(pin):
    pin = decode_pin_name(pin)
    with open('/sys/class/gpio/gpio' + str(pin) + '/value', 'r') as f:
        reading = f.read()
    return reading.strip()

# Configures the specified pin to behave either as an input or an output
# E.g. pinMode('5', 'INPUT')
def pinMode(pin, mode):
    pin = decode_pin_name(pin)
    with open('/sys/class/gpio/gpio' + str(pin) + '/direction', 'w') as f:
        if (mode == 'INPUT'):
            f.write('in')
        else:
            f.write('out')

# Called with list of pins [ 'LED' ]
# Returns dictionary of tuples { 'pin': (direction, value) }
def readPins(pinlist):
    pins = {}
    for pin in pinlist:
        syspin = str(decode_pin_name(pin))
        try:
            with open('/sys/class/gpio/gpio' + syspin + '/direction', 'r') as f:
                direction = f.read().strip()
            with open('/sys/class/gpio/gpio' + syspin + '/value', 'r') as f:
                value = f.read()
            pins[pin] = (direction.strip(), value.strip())
        except:
            print ('## readPins ## Cannot access pin {0} ({1})'.format(pin, syspin))
    return pins

