from yel_utils import InputCommand

class Command(InputCommand):

    def on_data(self, data):
        self.printer(bool(data))

def run(options, din, dout):
    cmd = Command(options, din, dout)
    return cmd.run()
