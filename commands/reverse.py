from yel_utils import InputCommand

class Command(InputCommand):

    def __init__(self, options, din, dout):
        InputCommand.__init__(self, options, din, dout)
        self.accum = []

    def on_end(self):
        for item in self.accum[::-1]:
            self.printer(item)

    def on_data(self, data):
        self.accum.append(data)

def run(options, din, dout):
    cmd = Command(options, din, dout)
    return cmd.run()
