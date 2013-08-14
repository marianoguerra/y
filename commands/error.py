import sys
from yel_utils import make_printer, Error
from yel_status import OK

def run(options, din, dout):
    printer = make_printer(dout)
    reason = options.get("reason", None)
    status = options.get("status", 500)

    printer(Error(dict(reason=reason, status=status)))

    return OK
    
