import serial, subprocess

def set_pin_high(pin):
    command = 'echo 1 > /sys/class/gpio/gpio' + str(pin) + '/value'
    subprocess.Popen(command, shell=True)

def set_pin_low(pin):
    command = 'echo 0 > /sys/class/gpio/gpio' + str(pin) + '/value'
    subprocess.Popen(command, shell=True)

def read_pin(pin):
    command = 'cat /sys/class/gpio/gpio' + str(pin) + '/value'
    state = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    return state.communicate()[0].strip() # The [0] selects stdout
                                          # ([1] would access stderr)

def send_serial(text):
    ser = serial.Serial('/dev/ttyS1', 19200, timeout=1)
    ser.write(str(text[0:80]))
    ser.close()
