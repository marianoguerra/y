from yel_utils import InputCommand

class Command(InputCommand):

    def __init__(self, options, din, dout):
        InputCommand.__init__(self, options, din, dout)
        self.accum = []

    def on_end(self):
        start = self.options.get("start", 0)
        stop = self.options.get("stop", None)
        step = self.options.get("step", 1)

        for item in self.accum[start:stop:step]:
            self.printer(item)

    def on_data(self, data):
        # TODO: make it the optimized way (counting and ending when
        # the slice is finished)
        self.accum.append(data)

def run(options, din, dout):
    cmd = Command(options, din, dout)
    return cmd.run()
