import sys
from yel_utils import make_printer, Error
from yel_status import OK

def run(options, din, dout):
    printer = make_printer(dout)
    start = options.get("start", 0)
    stop = options.get("stop", 10)
    step = options.get("step", 1)

    printer(list(range(start, stop, step)))

    return OK
    
