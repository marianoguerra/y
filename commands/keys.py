import sys
from yel_utils import TypeCommand

class ValuesCommand(TypeCommand):

    def __init__(self, options, din, dout):
        TypeCommand.__init__(self, dict, lambda x: x.keys(), options,
                din, dout)

def run(options=None, din=sys.stdin, dout=sys.stdout):
    cmd = ValuesCommand(options, din, dout)
    return cmd.run()
