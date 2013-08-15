import psutil

from yel_utils import make_printer
from yel_status import OK

def run(options, din, dout):
    printer = make_printer(dout)

    for iface, item in psutil.net_io_counters(pernic=True).items():
        data = item._asdict()
        data["name"] = iface
        printer(data)

    return OK
    
