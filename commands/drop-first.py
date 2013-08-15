from yel_utils import InputCommand

class Command(InputCommand):

    def __init__(self, options, din, dout):
        InputCommand.__init__(self, options, din, dout)
        self.count = self.options.get("value", 1)
        self.items_count = 0

    def on_data(self, data):
        if self.items_count >= self.count:
            self.printer(data)

        self.items_count += 1

def run(options, din, dout):
    cmd = Command(options, din, dout)
    return cmd.run()
