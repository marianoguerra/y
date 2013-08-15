import sys
from yel_utils import InputCommand

class Command(InputCommand):

    def __init__(self, options, din, dout):
        InputCommand.__init__(self, options, din, dout)
        self.count = self.options.get("value", 1)
        self.accum = []

    def on_end(self):
        for item in self.accum:
            self.printer(item)

    def on_data(self, data):
        if len(self.accum) < self.count:
            self.accum.append(data)

def run(options=None, din=sys.stdin, dout=sys.stdout):
    cmd = Command(options, din, dout)
    return cmd.run()
