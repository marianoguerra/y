import os
import pwd
import grp
import sys
import imp
import edn_format
import datetime
import collections

from edn_format.edn_parse import TaggedElement
from edn_format.edn_lex import Symbol, Keyword

from yel_status import OK, NOT_FOUND
from yel_predicates import *

END_UNIT = "\n"

CACHED_USER_NAMES  = {}
CACHED_GROUP_NAMES = {}

path = [os.path.join(os.path.dirname(__file__), 'commands')]

def import_command(name, path):
    file_, pathname, description = imp.find_module(name, path)
    module = imp.load_module(name, file_, pathname, description)
    file_.close()
    return module


def run_command(name, args, path, is_map=False, din=None, dout=None):
    global END_UNIT
    try:
        command = import_command(name, path)
        default_param = getattr(command, "DEFAULT_PARAM", "value")

        if isinstance(args, dict):
            dict_options = args 
            wrapped = False
        else:
            dict_options = {default_param: args}
            wrapped = True

        options = Options(dict_options, wrapped)
        dout = dout if dout is not None else sys.stdout

        if is_map:
            # TODO
            real_end_unit = END_UNIT
            END_UNIT = " "

            skip, end, data = next_data(sys.stdin, dout)

            while not end:
                if skip:
                    continue
                data_is_seq = is_seq(data)

                if data_is_seq:
                    dout.write("[")

                din = LineMapper(data)
                command.run(options, din, dout)

                if data_is_seq:
                    dout.write("]")

                dout.write(real_end_unit)

                skip, end, data = next_data(sys.stdin, dout)

            END_UNIT = real_end_unit
        else:
            din = din if din is not None else sys.stdin

        status = command.run(options, din, dout)
        dout.flush()
        return status
    except ImportError:
        error("Command '{}' not found".format(name), NOT_FOUND)


def eval_field(field, data, printer, error):
    if isinstance(field, tuple):
        if len(field) == 0:
            return None
        else:
            command = field[0]
            args = field[1:] if len(field) > 2 else field[1]
            dout = DataOut()
            din = LineMapper([data])
            run_command(command, args, path, False, din, dout)
            result_str = dout.units[0] if dout.units else None
            result = pythonify(edn_format.loads(result_str))
            return result
    else:
        return data

def get_user_from_uid(uid):
    if uid in CACHED_USER_NAMES:
        return CACHED_USER_NAMES[uid]
    else:
        try:
            username = pwd.getpwuid(uid)[0]
        except KeyError:
            return str(uid)

        CACHED_USER_NAMES[uid] = username
        return username

def get_group_from_gid(gid):
    if gid in CACHED_GROUP_NAMES:
        return CACHED_GROUP_NAMES[gid]
    else:
        try:
            groupname = grp.getgrgid(gid)[0]
        except KeyError:
            return str(gid)

        CACHED_GROUP_NAMES[gid] = groupname
        return groupname

def unwrap(data):
    if isinstance(data, TaggedValue):
        return data.value
    else:
        return data

def to_list(data):
    if is_seq(data):
        return data
    else:
        return [data]

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

def transform_seq(obj, visitor):
    return [transform(item, visitor) for item in visitor(obj)]

def transform(obj, visitor):
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            new_key = visitor(key)
            new_value = visitor(value)
            result[new_key] = new_value

        return result
    elif isinstance(obj, list):
        return transform_seq(obj, visitor)
    elif isinstance(obj, tuple):
        return tuple(transform_seq(obj, visitor))
    elif isinstance(obj, set):
        return set(transform_seq(obj, visitor))
    else:
        return visitor(obj)


def pythonify_seq(obj):
    result = []
    for value in obj:
        new_value = pythonify(value)
        result.append(new_value)

    return result

class StrSymbol(str):
    pass

class StrKeyword(str):
    pass

def pythonify(obj):
    if isinstance(obj, Symbol):
        return StrSymbol(obj)
    elif isinstance(obj, Keyword):
        return StrKeyword(str(obj)[1:])
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

    def on_start(self):
        pass

    def on_end(self):
        pass

    def run(self):
        self.on_start()
        try:
            skip, end, data = next_data(self.din, self.dout)
            while not self.finish and not end:
                if skip:
                    continue

                if isinstance(data, Options):
                    self.on_options(data)
                else:
                    self.on_data(data)

                skip, end, data = next_data(self.din, self.dout)

            self.on_end()
        except KeyboardInterrupt:
            pass

        return self.status

class LineMapper(object):
    
    def __init__(self, data):
        self.remaining = to_list(data)

    def next_data(self):
        if len(self.remaining) > 0:
            return False, False, self.remaining.pop(0)
        else:
            return False, True, None

class DataOut(object):

    def __init__(self):
        self.units = []

    def write(self, data):
        if data != END_UNIT:
            self.units.append(pythonify(data))

    def flush(self):
        pass

def next_data(din, dout):
    skip = False
    data = None

    if isinstance(din, LineMapper):
        return din.next_data()

    unit = din.readline()
    end = not bool(unit)

    if end:
        return skip, end, data

    try:
        data = edn_format.loads(unit)
    except SyntaxError as err:
        print_error(str(err), 500, dout)
        skip = True

    return skip, end, data

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

    def __eq__(self, other):
        if isinstance(other, TaggedValue):
            return self.value == other.value
        else:
            return self.value == other

    def to_human(self):
        return str(self.value)

class TaggedString(TaggedValue):
    def __str__(self):
        # TODO: escape quotes
        return '{} "{}"'.format(self.name, self.value)

class FileSize(TaggedValue):
    
    def __init__(self, value):
        TaggedValue.__init__(self, "#y.FileSize", value)

    def to_human(self):
        return "{} KBs".format(self.value / 1024)

class Uid(TaggedValue):
    
    def __init__(self, value):
        TaggedValue.__init__(self, "#y.Uid", value)

    def to_human(self):
        return get_user_from_uid(self.value)

class Gid(TaggedValue):
    
    def __init__(self, value):
        TaggedValue.__init__(self, "#y.Gid", value)

    def to_human(self):
        return get_group_from_gid(self.value)

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

    def to_human(self):
        dtime = datetime.datetime.fromtimestamp(self.value)
        return dtime.strftime("%c")


class FileType(TaggedString):
    TO_HUMAN = {
        "f": "File",
        "d": "Dir",
        "l": "Link",
        "m": "Mount"
    }

    def __init__(self, value):
        TaggedString.__init__(self, "#y.FileType", value)

    def to_human(self):
        return self.TO_HUMAN.get(self.value, "Unknwon")

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
