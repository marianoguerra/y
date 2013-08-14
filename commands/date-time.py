import datetime

from yel_utils import make_printer
from yel_status import OK

def run(options, din, dout):
    printer = make_printer(dout)
    now = datetime.datetime.now()
    printer(dict(year=now.year, month=now.month, day=now.day, hours=now.hour,
        minute=now.minute, second=now.second))
    return OK
