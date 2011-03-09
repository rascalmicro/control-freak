import daemon

from rascal import analogger

with daemon.DaemonContext():
    analogger()

