import os
import sys
import edn_format
import collections

from edn_format.edn_parse import TaggedElement
from edn_format.edn_lex import Symbol, Keyword

from yel_status import OK

END_UNIT = "\n"

def get_key(data, key, default):
    if isinstance(data, collections.Sequence):
        if key in data:
            return data[key]
        else:
            return default
    elif isinstance(data, collections.Mapping):
        return data.get(key, default)
    else:
        return default

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
    def printer(obj, add_end_unit=True):
        out.write(edn_format.dumps(obj))

        if add_end_unit:
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
        self.status = OK
        self.finish = False

        self.on_options(options)

    def end(self, status=OK):
        self.finish = True
        self.status = status

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
            while not self.finish and unit:
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

        return self.status

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

class TaggedValue(TaggedElement):
    def __init__(self, name, value):
        self.value = value
        self.name = name

    def __str__(self):
        return "{} {}".format(self.name, self.value)

    __repr__ = __str__

    def __hash__(self):
        return hash(self.value)

    def __cmp__(self, other):
        if isinstance(other, TaggedValue):
            return cmp(self.value, other.value)
        else:
            return cmp(self.value, other)

class TaggedString(TaggedValue):
    def __str__(self):
        # TODO: escape quotes
        return '{} "{}"'.format(self.name, self.value)

class FileSize(TaggedValue):
    
    def __init__(self, value):
        TaggedValue.__init__(self, "#y.FileSize", value)

class Uid(TaggedValue):
    
    def __init__(self, value):
        TaggedValue.__init__(self, "#y.Uid", value)

class Gid(TaggedValue):
    
    def __init__(self, value):
        TaggedValue.__init__(self, "#y.Gid", value)

class Path(TaggedString):
    
    def __init__(self, value):
        TaggedValue.__init__(self, "#y.Path", value)

class UnixPerms(TaggedValue):
    def __init__(self, value):
        TaggedValue.__init__(self, "#y.UnixPerms", value)

    def __str__(self):
        return '{} "{}"'.format(self.name, self.value)

    __repr__ = __str__

class Timestamp(TaggedValue):

    def __init__(self, value):
        TaggedValue.__init__(self, "#y.Timestamp", value)

class FileType(TaggedString):

    def __init__(self, value):
        TaggedString.__init__(self, "#y.FileType", value)

class File(dict, TaggedElement):

    def __init__(self, value):
        self.update(value)
        self.name = "#y.File"

    @classmethod
    def from_path(cls, fpath):
        stat = os.stat(fpath)
        size = FileSize(stat.st_size)
        uid = Uid(stat.st_uid)
        gid = Gid(stat.st_gid)
        atime = Timestamp(stat.st_atime)
        mtime = Timestamp(stat.st_mtime)
        mode = UnixPerms(oct(stat.st_mode))
        path = Path(os.path.abspath(fpath))

        if os.path.isfile(fpath):
            ftype = "f"
        elif os.path.isdir(fpath):
            ftype = "d"
        elif os.path.islink(fpath):
            ftype = "l"
        elif os.path.ismount(fpath):
            ftype = "m"
        else:
            ftype = "?"

        file_type = FileType(ftype)

        return cls(dict(path=path, size=size, uid=uid, gid=gid, atime=atime,
            mtime=mtime, mode=mode, type=file_type))

    def __str__(self):
        return "#y.File {}".format(edn_format.dumps(self.to_dict()))

    def to_dict(self):
        return dict(self.items())

edn_format.add_tag("y.E", Error)
edn_format.add_tag("y.O", Options)
edn_format.add_tag("y.Uid", Uid)
edn_format.add_tag("y.Gid", Gid)
edn_format.add_tag("y.File", File)
edn_format.add_tag("y.FileSize", FileSize)
edn_format.add_tag("y.FileType", FileType)
edn_format.add_tag("y.Path", Path)
edn_format.add_tag("y.Timestamp", Timestamp)
edn_format.add_tag("y.UnixPerms", UnixPerms)
