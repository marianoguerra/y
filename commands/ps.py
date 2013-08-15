import psutil

from yel_utils import make_printer
from yel_status import OK

def run(options, din, dout):
    printer = make_printer(dout)

    for pid in psutil.get_pid_list():
        printer(psutil.Process(pid).as_dict())

    return OK
    
