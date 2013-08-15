from yel_utils import InputCommand

class Command(InputCommand):

    def on_end(self):
        if not self.finish:
            self.printer(True)

    def on_data(self, data):
        if not bool(data): 
            self.end()
            self.printer(False)

def run(options, din, dout):
    cmd = Command(options, din, dout)
    return cmd.run()
