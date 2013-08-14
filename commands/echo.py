import sys
from yel_utils import make_printer
from yel_status import OK

def run(options, din, dout):
    printer = make_printer(dout)

    if options.wrapped:
        printer(options.get("value", None))
    else:
        printer(options.to_dict())

    return OK
    
