import sys
from yel_utils import InputCommand

class Command(InputCommand):

    def __init__(self, options, din, dout):
        InputCommand.__init__(self, options, din, dout)
        self.value = self.options.get("value", 1)
        self.items_count = 0
        self.accum = None

    def on_end(self):
        self.printer(self.accum)

    def on_data(self, data):
        self.items_count += 1

        if self.items_count == self.value:
            self.accum = data

def run(options=None, din=sys.stdin, dout=sys.stdout):
    cmd = Command(options, din, dout)
    return cmd.run()
