import rascal
from time import sleep, time

def do_main_program():

    while(1):
        reading0 = str(float(rascal.read_analog(0)) * 3.3 / 1024.0)
        reading1 = str(float(rascal.read_analog(1)) * 3.3 / 1024.0)
        reading2 = str(float(rascal.read_analog(2)) * 3.3 / 1024.0)
        reading3 = str(float(rascal.read_analog(3)) * 3.3 / 1024.0)
        f = open('/home/root/ana.log', 'a')
        f.write(','.join([str(time()), reading0, reading1, reading2, reading3]) + '\n')
        f.close()
        sleep(1)

