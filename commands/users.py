import psutil

from yel_utils import make_printer
from yel_status import OK

def run(options, din, dout):
    printer = make_printer(dout)

    for item in psutil.get_users():
        printer(item._asdict())

    return OK
    
