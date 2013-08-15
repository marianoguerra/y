from yel_utils import InputCommand

class CountCommand(InputCommand):

    def __init__(self, options, din, dout):
        InputCommand.__init__(self, options, din, dout)
        self.count = 0

    def on_end(self):
        self.printer(self.count)

    def on_data(self, data):
        self.count += 1

def run(options, din, dout):
    cmd = CountCommand(options, din, dout)
    return cmd.run()
