import sys
from yel_utils import TypeCommand
import collections

class CountCommand(TypeCommand):

    def __init__(self, options, din, dout):
        TypeCommand.__init__(self, collections.Sized, len, options,
                din, dout)

def run(options=None, din=sys.stdin, dout=sys.stdout):
    cmd = CountCommand(options, din, dout)
    return cmd.run()
