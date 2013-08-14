import sys
from yel_utils import TypeCommand

class Command(TypeCommand):

    def __init__(self, options, din, dout):
        TypeCommand.__init__(self, list, self.fun, options,
                din, dout)

    def fun(self, data):
        value = self.options.get("value", [])
        return list(data) + list(value)

def run(options=None, din=sys.stdin, dout=sys.stdout):
    cmd = Command(options, din, dout)
    return cmd.run()
