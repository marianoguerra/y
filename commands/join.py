import sys
from yel_utils import TypeCommand
import collections

class Command(TypeCommand):

    def __init__(self, options, din, dout):
        TypeCommand.__init__(self, collections.Iterable, self.fun, options,
                din, dout)

    def fun(self, data):
        sep = self.options.get("sep", "")
        return sep.join([str(x) for x in data])

def run(options=None, din=sys.stdin, dout=sys.stdout):
    cmd = Command(options, din, dout)
    return cmd.run()
