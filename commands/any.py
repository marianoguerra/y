from yel_utils import InputCommand

class Command(InputCommand):

    def on_end(self):
        if not self.finish:
            self.printer(False)

    def on_data(self, data):
        if bool(data): 
            self.end()
            self.printer(True)

def run(options, din, dout):
    cmd = Command(options, din, dout)
    return cmd.run()
