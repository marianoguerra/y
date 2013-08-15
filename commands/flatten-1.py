from yel_utils import InputCommand
import collections

class Command(InputCommand):

    def on_data(self, data):
        if isinstance(data, collections.Iterable):
            for item in data:
                self.printer(item)
        else:
            self.printer(data)

def run(options, din, dout):
    cmd = Command(options, din, dout)
    return cmd.run()
