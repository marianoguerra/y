from yel_utils import InputCommand, TaggedValue

class Command(InputCommand):

    def __init__(self, options, din, dout):
        InputCommand.__init__(self, options, din, dout)
        self.accum = {}

    def on_end(self):
        self.printer(self.accum)

    def on_data(self, data):
        key_name = self.options.get("value", "value")
        key = data[key_name]

        if isinstance(key, TaggedValue):
            key = key.value

        bucket = self.accum.get(key, None)

        if bucket is None:
            self.accum[key] = [data]
        else:
            self.accum[key].append(data)

def run(options, din, dout):
    cmd = Command(options, din, dout)
    return cmd.run()
