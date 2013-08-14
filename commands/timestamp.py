import time

from yel_utils import make_printer
from yel_status import OK

def run(options, din, dout):
    printer = make_printer(dout)
    timestamp = time.time()
    printer(dict(timestamp=timestamp))
    return OK
