from yel_utils import InputCommand
import collections

class Command(InputCommand):

    def __init__(self, options, din, dout):
        InputCommand.__init__(self, options, din, dout)
        self.count = self.options.get("value", 1)
        self.accum = collections.deque(maxlen=self.count)

    def on_data(self, data):
        if len(self.accum) == self.count:
            old_data = self.accum.popleft()
            self.printer(old_data)

        self.accum.append(data)

def run(options, din, dout):
    cmd = Command(options, din, dout)
    return cmd.run()
