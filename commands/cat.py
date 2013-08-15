import json

from yel_utils import to_list, error, END_UNIT
from yel_status import OK

def run(options, din, dout):
    files = to_list(options.get("value", []))

    for file_ in files:
        try:
            with open(file_) as handle:
                for line in handle:
                    dout.write(json.dumps(line))
                    dout.write(END_UNIT)
        except IOError:
            error("Error opening file '{}'".format(file_), 404, dout)

    return OK
