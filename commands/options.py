import sys
from yel_utils import InputCommand

class Command(InputCommand):

    def on_options(self, options):
        InputCommand.on_options(self, options)
        self.printer(options)

    def on_data(self, data):
        self.printer(data)

def run(options=None, din=sys.stdin, dout=sys.stdout):
    cmd = Command(options, din, dout)
    return cmd.run()
