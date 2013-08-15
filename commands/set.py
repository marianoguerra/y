from yel_utils import InputCommand

class SetCommand(InputCommand):

    def __init__(self, options, din, dout):
        InputCommand.__init__(self, options, din, dout)
        self.set = set()

    def on_end(self):
        for item in self.set:
            self.printer(item)

    def on_data(self, data):
        self.set.add(data)

def run(options, din, dout):
    cmd = SetCommand(options, din, dout)
    return cmd.run()
