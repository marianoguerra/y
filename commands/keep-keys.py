from yel_utils import TypeCommand

class Command(TypeCommand):

    def __init__(self, options, din, dout):
        TypeCommand.__init__(self, dict, self.fun, options,
                din, dout)

    def fun(self, data):
        keys = set(self.options.get("value", []))
        data_keys = set(data.keys())
        to_drop = data_keys.difference(keys)

        for key in to_drop:
            del data[key]

        return data

def run(options, din, dout):
    cmd = Command(options, din, dout)
    return cmd.run()
