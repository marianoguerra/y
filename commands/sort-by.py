from yel_utils import InputCommand, get_key
import random

class Command(InputCommand):

    def __init__(self, options, din, dout):
        InputCommand.__init__(self, options, din, dout)
        self.accum = []
        self.key = self.options.get("value", "value")

    def cmp(self, a, b):
        val_a = get_key(a, self.key, None)
        val_b = get_key(b, self.key, None)

        return cmp(val_a, val_b)

    def on_end(self):
        for item in sorted(self.accum, self.cmp):
            self.printer(item)

    def on_data(self, data):
        self.accum.append(data)

def run(options, din, dout):
    cmd = Command(options, din, dout)
    return cmd.run()
