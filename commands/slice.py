import sys
from yel_utils import TypeCommand
import collections

class Command(TypeCommand):

    def __init__(self, options, din, dout):
        TypeCommand.__init__(self, collections.Iterable, self.fun, options,
                din, dout)

    def fun(self, data):
        start = self.options.get("start", 0)
        stop = self.options.get("stop", None)
        step = self.options.get("step", 1)

        return data[start:stop:step]

def run(options=None, din=sys.stdin, dout=sys.stdout):
    cmd = Command(options, din, dout)
    return cmd.run()
