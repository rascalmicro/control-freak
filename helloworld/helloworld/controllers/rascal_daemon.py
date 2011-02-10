import daemon, rascal

with daemon.DaemonContext():
    do_main_program()

def do_main_program():
    while(1):
        state = rascal.read_pin(66)
        f = open('logfile', 'a')
        f.write(state + '\n')
        f.close
        sleep(1)

