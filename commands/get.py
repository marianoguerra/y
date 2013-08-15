from yel_utils import TypeCommand
import collections

class Command(TypeCommand):

    def __init__(self, options, din, dout):
        TypeCommand.__init__(self,
            (collections.Sequence, collections.Mapping), self.fun, options,
            din, dout)

    def fun(self, data):
        key = self.options.get("value", "value")

        if isinstance(data, collections.Sequence):
            if key in data:
                return data[key]
            else:
                return None
        else:
            return data.get(key, None)

def run(options, din, dout):
    cmd = Command(options, din, dout)
    return cmd.run()
