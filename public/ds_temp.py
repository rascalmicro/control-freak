# dsmall 2 Jan 2012
def read_sensor(address):
    import subprocess
    cmd = 'i2cget -y 0 ' + hex(address) + ' 0x00 w'
    subp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    try:
        data = int(subp.communicate()[0].strip(), 16)
    except ValueError:
        print 'Couldn\'t get reading from sensor'
        return float('NaN')
    return ((data % 0x0100 * 16) + (data / 0x1000)) * 0.0625
