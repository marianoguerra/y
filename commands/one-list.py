import sys
from yel_utils import InputCommand

class Command(InputCommand):

    def __init__(self, options, din, dout):
        InputCommand.__init__(self, options, din, dout)
        self.accum = []

    def on_end(self):
        self.printer(self.accum)

    def on_data(self, data):
        self.accum.append(data)

def run(options=None, din=sys.stdin, dout=sys.stdout):
    cmd = Command(options, din, dout)
    return cmd.run()
