import sys
from yel_utils import InputCommand

class SetCommand(InputCommand):

    def on_data(self, data):
        if isinstance(data, (tuple, set, list)):
            result = set(data)
        else:
            result = set([data])

        self.printer(result)

def run(options=None, din=sys.stdin, dout=sys.stdout):
    cmd = SetCommand(options, din, dout)
    return cmd.run()
