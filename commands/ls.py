import os
from yel_utils import make_printer, File
from yel_status import OK

def run(options, din, dout):
    printer = make_printer(dout)
    path = options.get("value", ".")

    if os.path.isdir(path):
        for _dirpath, dirnames, filenames in os.walk(path):

            for dirname in dirnames:
                printer(File.from_path(dirname))

            for filename in filenames:
                printer(File.from_path(filename))

            break

    else:
        printer(File.from_path(path))

    return OK
    
