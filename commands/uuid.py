import uuid

from yel_utils import make_printer
from yel_status import OK

def run(options, din, dout):
    printer = make_printer(dout)
    printer(dict(uuid=uuid.uuid4()))
    return OK
