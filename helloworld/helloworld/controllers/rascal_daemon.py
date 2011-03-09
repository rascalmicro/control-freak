import daemon

from analog import do_main_program

with daemon.DaemonContext():
    do_main_program()

