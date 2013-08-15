from yel_utils import InputCommand, END_UNIT

class Command(InputCommand):

    def __init__(self, options, din, dout):
        InputCommand.__init__(self, options, din, dout)
        self.first = True

    def on_end(self):
        self.dout.write('"')
        self.dout.write(END_UNIT)

    def on_data(self, data):
        if self.first:
            self.first = False
            self.dout.write('"')
        else:
            sep = self.options.get("sep", "")
            self.dout.write(sep)

        self.dout.write(str(data))


def run(options, din, dout):
    cmd = Command(options, din, dout)
    return cmd.run()
