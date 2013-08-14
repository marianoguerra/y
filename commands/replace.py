import sys
from yel_utils import TypeCommand, pythonify
from edn_format.edn_lex import Symbol, Keyword

class Command(TypeCommand):

    def __init__(self, options, din, dout):
        TypeCommand.__init__(self, (str, Symbol, Keyword), self.fun, options,
                din, dout)

    def fun(self, data):
        old = self.options.get("old", None)
        new = self.options.get("new", "")
        as_string = pythonify(data)

        if old is None:
            return as_string
        else:
            return as_string.replace(old, new)

def run(options=None, din=sys.stdin, dout=sys.stdout):
    cmd = Command(options, din, dout)
    return cmd.run()
