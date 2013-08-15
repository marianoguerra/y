from yel_utils import InputCommand

class CountCommand(InputCommand):

    def __init__(self, options, din, dout):
        InputCommand.__init__(self, options, din, dout)
        self.min = None

    def on_end(self):
        self.printer(self.min)

    def on_data(self, data):
        if self.min is None or self.min > data:
            self.min = data

def run(options, din, dout):
    cmd = CountCommand(options, din, dout)
    return cmd.run()
