import rascal
from time import sleep, time

def do_main_program():

    while(1):
        reading0 = rascal.read_analog(0)
        reading1 = rascal.read_analog(1)
        reading2 = rascal.read_analog(2)
        reading3 = rascal.read_analog(3)
        f = open('/home/root/ana.log', 'a')
        f.write(','.join([str(time()), reading0, reading1, reading2, reading3]) + '\n')
        f.close()
        sleep(1)

