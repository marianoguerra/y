from yel_utils import InputCommand

class CountCommand(InputCommand):

    def __init__(self, options, din, dout):
        InputCommand.__init__(self, options, din, dout)
        self.max = None

    def on_end(self):
        self.printer(self.max)

    def on_data(self, data):
        if self.max is None or self.max < data:
            self.max = data

def run(options, din, dout):
    cmd = CountCommand(options, din, dout)
    return cmd.run()
