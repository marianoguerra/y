import psutil

from yel_utils import make_printer
from yel_status import OK

def run(options, din, dout):
    printer = make_printer(dout)

    for partition in psutil.disk_partitions():
        printer(partition._asdict())

    return OK
    
