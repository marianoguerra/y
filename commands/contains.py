import sys
from yel_utils import TypeCommand, pythonify
from edn_format.edn_lex import Symbol, Keyword

class Command(TypeCommand):

    def __init__(self, options, din, dout):
        TypeCommand.__init__(self, (str, Symbol, Keyword), self.fun, options,
                din, dout)

    def fun(self, data):
        value = self.options.get("value", None)
        if value is None:
            return False
        else:
            return str(value) in pythonify(data)

def run(options=None, din=sys.stdin, dout=sys.stdout):
    cmd = Command(options, din, dout)
    return cmd.run()
