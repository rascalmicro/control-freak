import subprocess

def set_pin_high(pin):
    command = 'echo 1 > /sys/class/gpio/gpio' + str(pin) + '/value'
    subprocess.Popen(command, shell=True)

def set_pin_low(pin):
    command = 'echo 0 > /sys/class/gpio/gpio' + str(pin) + '/value'
    subprocess.Popen(command, shell=True)
