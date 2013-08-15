from yel_utils import TypeCommand

class Command(TypeCommand):

    def __init__(self, options, din, dout):
        TypeCommand.__init__(self, dict, self.fun, options,
                din, dout)

    def fun(self, data):
        keys = self.options.get("value", [])

        for key in keys:
            del data[key]

        return data

def run(options, din, dout):
    cmd = Command(options, din, dout)
    return cmd.run()
