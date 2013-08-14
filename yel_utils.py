import sys
import edn_format

from edn_format.edn_parse import TaggedElement
from edn_format.edn_lex import Symbol, Keyword

from yel_status import OK

END_UNIT = "\n"

def pythonify_seq(obj):
    result = []
    for value in obj:
        new_value = pythonify(value)
        result.append(new_value)

    return result

def pythonify(obj):
    if isinstance(obj, Symbol):
        return str(obj)
    elif isinstance(obj, Keyword):
        return str(obj)[1:]
    elif isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            new_key = pythonify(key)
            new_value = pythonify(value)
            result[new_key] = new_value

        return result
    elif isinstance(obj, list):
        return pythonify_seq(obj)
    elif isinstance(obj, tuple):
        return tuple(pythonify_seq(obj))
    elif isinstance(obj, set):
        return set(pythonify_seq(obj))
    else:
        return obj

def make_printer(out):
    def printer(obj):
        out.write(edn_format.dumps(obj))
        out.write(END_UNIT)

    return printer

class Options(dict, TaggedElement):
    def __init__(self, value, wrapped=False):
        self.name = "y.O"
        self.update(value)
        self.wrapped = wrapped

    def __str__(self):
        return "#y.O {}".format(edn_format.dumps(self.to_dict()))

    def to_dict(self):
        return dict(self.items())

class Error(TaggedElement):
    def __init__(self, value):
        self.name = "y.E"
        self.value = value

    def __str__(self):
        return "#y.E {}".format(edn_format.dumps(self.value))

class InputCommand(object):

    def __init__(self, options, din, dout):
        self.printer = make_printer(dout)
        self.din = din
        self.dout = dout
        self.options = None

        self.on_options(options)

    def on_options(self, options):
        self.options = pythonify(options)

    def on_data(self, data):
        self.printer(data)

    def on_error(self, error):
        self.printer(error)

    def error(self, reason, status=500):
        print_error(reason, status, self.dout)

    def on_end(self):
        pass

    def run(self):
        try:
            unit = self.din.readline()
            while unit:
                try:
                    data = edn_format.loads(unit)
                except SyntaxError as error:
                    print_error(str(error), 500, self.dout)
                    unit = self.din.readline()
                    continue

                if isinstance(data, Options):
                    self.on_options(data)
                else:
                    self.on_data(data)

                unit = self.din.readline()

            self.on_end()
        except KeyboardInterrupt:
            pass

        return OK

class TypeCommand(InputCommand):

    def __init__(self, type_, fun, options, din, dout):
        InputCommand.__init__(self, options, din, dout)
        self.type = type_
        self.fun = fun

        if type(type_) != tuple:
            self.type_name = type_.__name__
        else:
            self.type_name = ", ".join(x.__name__ for x in type_)

    def on_data(self, data):
        if isinstance(data, self.type):
            self.printer(self.fun(data))
        else:
            self.error("Data is not of type {}: {}".format(
                self.type_name, type(data).__name__),
                    400)

class StrCommand(TypeCommand):

    def __init__(self, method_name, options, din, dout):
        TypeCommand.__init__(self, (str, Keyword, Symbol),
                lambda x: getattr(pythonify(x), method_name)(), options,
                din, dout)

def print_error(reason, status, out):
    err = Error(dict(reason=reason, status=status))
    out.write(edn_format.dumps(err))
    out.write(END_UNIT)

def error(reason, status, out=sys.stdout):
    print_error(reason, status, out)
    sys.exit(status)

edn_format.add_tag("y.E", Error)
edn_format.add_tag("y.O", Options)
