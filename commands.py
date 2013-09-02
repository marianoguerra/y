import edn
import yutil
import psutil
import uuid

from predicates import PREDICATES
from ystatus import NOT_FOUND, BAD_REQUEST, OK

from ytypes import *

import time
import random
import datetime
import collections

class Handler(object):
    def __init__(self, din, on_data=None, dout=None, emit_on_end=None,
            do_reset=True):
        self.count = 0
        self.accum = []
        self.dct = {}
        self.value = None
        self.dout = dout
        self.emit_on_end = emit_on_end
        self.do_reset = do_reset

        din.on_end(self._on_end)

        if on_data:
            din.on_data(on_data)
            din.consume()

    def _on_end(self):
        if self.emit_on_end:
            self.dout.emit(getattr(self, self.emit_on_end))

        if self.do_reset:
            self.reset()

    def reset(self):
        self.count = 0
        self.accum = []
        self.value = None
        self.dct = {}

def echo(args, din, dout, raw_args):
    dout.emit(args)

def cnot(args, din, dout, raw_args):
    Handler(din, lambda data: dout.emit(not bool(data)))

def cbool(args, din, dout, raw_args):
    Handler(din, lambda data: dout.emit(bool(data)))

def crange(args, din, dout, raw_args):
    start = args.get("from", 0)
    stop = args.get("to", 10)
    step = args.get("step", 1)

    for i in range(start, stop, step):
        dout.emit(i)

def _with_predicate(args, din, dout, raw_args, on_data):
    predicate_name = raw_args[0]
    predicate = PREDICATES.get(predicate_name, None)

    if predicate is None:
        return dout.error("Predicate not found: '{}'".format(predicate_name),
                NOT_FOUND)
    
    if not yutil.is_seq(args):
        param = args
    elif len(args) == 1:
        param = args[0]
    elif len(args) > 1:
        param = args
    else:
        param = None

    return Handler(din, lambda data: on_data(data, predicate, param))

def cis(args, din, dout, raw_args):
    def on_data(data, predicate, param):
        dout.emit(predicate(data, param))

    return _with_predicate(args, din, dout, raw_args, on_data)

cis.n_raw_args = 1
cis.reduce_command = True

def drop(args, din, dout, raw_args):
    def on_data(data, predicate, param):
        if not predicate(data, param):
            dout.emit(data)

    return _with_predicate(args, din, dout, raw_args, on_data)
          
drop.n_raw_args = 1

def keep(args, din, dout, raw_args):
    def on_data(data, predicate, param):
        if predicate(data, param):
            dout.emit(data)

    return _with_predicate(args, din, dout, raw_args, on_data)
          
keep.n_raw_args = 1

def cmap(args, din, dout, raw_args):
    name = args[0]
    command = yutil.load_command(name)

    if command is None:
        return dout.error("command '{}' not found".format(name), NOT_FOUND)

    reduce_command = getattr(command, "reduce_command", False)
    cmd_raw_args, parsed = yutil.parse_args(args[1:],
            getattr(command, "n_raw_args", 0))

    def on_data(data):
        subout = yutil.EdnWriter(dout.dout, sep=" ",
                write_sep_after_first=True)
        mapin = yutil.EdnIterator(data)
        if not reduce_command:
            dout.raw_write("[")

        command(parsed, mapin, subout, cmd_raw_args)

        if not reduce_command:
            dout.raw_write("]\n")
        else:
            dout.raw_write("\n")

    din.on_data(on_data)
    din.consume()

cmap.keep_args_raw = True

def str_op(op, requires_param=False, param_optional=True):
    def command(param, din, dout, raw_args):
        if param_optional and isinstance(param, dict) and len(param) == 0:
            param = None
        elif requires_param and not isinstance(param, str):
            return dout.error("Expected string argument", BAD_REQUEST)

        def on_data(data):
            if isinstance(data, str):
                if requires_param:
                    dout.emit(op(data, param))
                else:
                    dout.emit(op(data))
            else:
                dout.error("Value '{}' is not a string".format(edn.dumps(data)),
                        BAD_REQUEST)

        return Handler(din, on_data)

    return command

upper = str_op(str.upper)
lower = str_op(str.lower)
title = str_op(str.title)
capitalize = str_op(str.capitalize)
ltrim = str_op(str.lstrip, True, True)
rtrim = str_op(str.rstrip, True, True)
trim = str_op(str.strip, True, True)
split = str_op(str.split, True, True)
startswith = str_op(str.startswith, True, False)
endswith = str_op(str.endswith, True, False)

def cany(args, din, dout, raw_args):
    def on_data(data, predicate, param):
        if predicate(data, param):
            dout.emit(True)
            din.stop()

    din.on_end(lambda: not din.is_stopped() and dout.emit(False))
    return _with_predicate(args, din, dout, raw_args, on_data)

cany.n_raw_args = 1
cany.reduce_command = True

def call(args, din, dout, raw_args):
    def on_data(data, predicate, param):
        if not predicate(data, param):
            dout.emit(False)
            din.stop()

    din.on_end(lambda: not din.is_stopped() and dout.emit(True))
    return _with_predicate(args, din, dout, raw_args, on_data)

call.n_raw_args = 1
call.reduce_command = True

def nth(args, din, dout, raw_args):
    value = int(raw_args[0])
    handler = Handler(din)

    def on_data(data):
        handler.count += 1

        if value == handler.count:
            dout.emit(data)
            din.stop()

    def on_end():
        if not din.is_stopped():
            dout.emit(None)

    din.on_data(on_data)
    din.on_end(on_end)
    din.consume()

nth.n_raw_args = 1
nth.reduce_command = True

def cmin(args, din, dout, raw_args):
    handler = Handler(din, None, dout, emit_on_end="value")
    def on_data(data):
        if handler.value is None or data < handler.value:
            handler.value = data

    din.on_data(on_data)
    din.consume()

cmin.reduce_command = True

def cmax(args, din, dout, raw_args):
    handler = Handler(din, None, dout, emit_on_end="value")
    def on_data(data):
        if handler.value is None or data > handler.value:
            handler.value = data

    din.on_data(on_data)
    din.consume()

cmax.reduce_command = True

def contains(args, din, dout, raw_args):
    arg = args
    def on_data(data):
        if arg == data:
            dout.emit(True)
            din.stop()

    def on_end():
        if not din.is_stopped():
            dout.emit(False)

    din.on_data(on_data)
    din.on_end(on_end)

    din.consume()

contains.reduce_command = True

def count(args, din, dout, raw_args):
    handler = Handler(din, dout=dout, emit_on_end="count")
    def on_data(data):
        handler.count += 1

    din.on_data(on_data)
    din.consume()

count.reduce_command = True

def first(args, din, dout, raw_args):
    limit = args
    handler = Handler(din)
    def on_data(data):
        handler.count += 1

        if handler.count > limit:
            din.stop()
        else:
            dout.emit(data)

    din.on_data(on_data)
    din.consume()

def last(args, din, dout, raw_args):
    limit = args
    handler = Handler(din)
    handler.items = collections.deque(maxlen=limit)

    def on_data(data):
        handler.items.append(data)

    def on_end():
        for item in handler.items:
            dout.emit(item)

        handler.items = collections.deque(maxlen=limit)

    din.on_data(on_data)
    din.on_end(on_end)
    din.consume()

def drop_first(args, din, dout, raw_args):
    limit = args
    handler = Handler(din)

    def on_data(data):
        handler.count += 1

        if handler.count > limit:
            dout.emit(data)

    din.on_data(on_data)
    din.consume()

def drop_last(args, din, dout, raw_args):
    limit = args
    handler = Handler(din)
    handler.items = collections.deque(maxlen=limit)
    def on_data(data):
        if len(handler.items) >= limit:
            dout.emit(handler.items.popleft())

        handler.items.append(data)

    def on_end():
        handler.items = collections.deque(maxlen=limit)

    din.on_data(on_data)
    din.on_end(on_end)
    din.consume()

def keys(args, din, dout, raw_args):
    din.on_data(lambda data: dout.emit(list(data.keys())))
    din.consume()

def values(args, din, dout, raw_args):
    din.on_data(lambda data: dout.emit(list(data.values())))
    din.consume()

def date_time(args, din, dout, raw_args):
    now = datetime.datetime.now()
    #  TODO: tagged value
    dout.emit(dict(year=now.year, month=now.month, day=now.day,
        hours=now.hour, minute=now.minute, second=now.second))

def timestamp(args, din, dout, raw_args):
    dout.emit(time.time() * 1000)

def ls(args, din, dout, raw_args):
    # TODO: path
    path = "."

    if os.path.isdir(path):
        for _dirpath, dirnames, filenames in os.walk(path):

            for dirname in dirnames:
                dout.emit(File.from_path(dirname))

            for filename in filenames:
                dout.emit(File.from_path(filename))

            break

    else:
        dout.emit(File.from_path(path))

    return OK

def flatten(args, din, dout, raw_args):
    def on_data(data):
        if isinstance(data, collections.Iterable):
            for item in data:
                dout.emit(item)
        else:
            dout.emit(data)

    din.on_data(on_data)
    din.consume()

def list_op(op, is_in_place):
    def command(args, din, dout, raw_args):
        handler = Handler(din, do_reset=False)
        def on_data(data):
            handler.accum.append(data)

        def on_end():
            if is_in_place:
                op(handler.accum)
                accum = handler.accum
            else:
                accum = op(handler.accum)

            for item in accum:
                dout.emit(item)

            handler.reset()

        din.on_data(on_data)
        din.on_end(on_end)
        din.consume()

    return command

sort = list_op(sorted, False)
shuffle = list_op(random.shuffle, True)
reverse = list_op(list.reverse, True)
cset = list_op(set, False)
collapse = list_op(lambda l: [l], False)

def join(args, din, dout, raw_args):
    sep = args
    handler = Handler(din, do_reset=False)

    def on_data(data):
        handler.accum.append(data)

    def on_end():
        dout.emit(sep.join([edn.dumps(item) for item in handler.accum]))
        handler.reset()

    din.on_data(on_data)
    din.on_end(on_end)
    din.consume()

def error(args, din, dout, raw_args):
    dout.error(args.get("reason", "error"), args.get("status", 500))

def slice(args, din, dout, raw_args):
    start = args.get("from", 0)
    stop = args.get("to", 10)
    step = args.get("step", 1)
    handler = Handler(din)

    def on_data(data):
        if handler.count >= start and handler.count < stop and handler.count % step == 0:
            dout.emit(data)
        elif handler.count >= stop:
            din.stop()

        handler.count += 1

    din.on_data(on_data)
    din.consume()

def cat(args, din, dout, raw_args):
    files = yutil.to_list(args)

    for filename in files:
        try:
            with open(filename) as handle:
                for line in handle:
                    dout.emit(line)
        except IOError as error:
            dout.error(str(error))

def keep_keys(args, din, dout, raw_args):
    keys = args

    def on_data(data):
        if yutil.is_assoc(data):
            result = {}

            for key in keys:
                result[key] = data.get(key)

            dout.emit(result)
        else:
            dout.error("Expected map-like object", 400)

    din.on_data(on_data)
    din.consume()

def drop_keys(args, din, dout, raw_args):
    keys = set(args)

    def on_data(data):
        if yutil.is_assoc(data):
            result = {}

            for key in set(data.keys()).difference(keys):
                result[key] = data.get(key)

            dout.emit(result)
        else:
            dout.error("Expected map-like object", 400)

    din.on_data(on_data)
    din.consume()

def cget(args, din, dout, raw_args):
    def on_data(data):
        if yutil.is_seq(args):
            dout.emit([yutil.get(data, key) for key in args])
        elif yutil.is_assoc(args):
            dout.emit({key: yutil.get(data, key, default) for key, default in args.items()})
        else:
            key = args
            dout.emit(yutil.get(data, key))

    din.on_data(on_data)
    din.consume()

def sort_by(args, din, dout, raw_args):
    key = args
    handler = Handler(din, do_reset=False)
    def on_data(data):
        handler.accum.append(data)

    def mycmp(a):
        return yutil.get(a, key)

    def on_end():
        for item in sorted(handler.accum, key=mycmp):
            dout.emit(item)

        handler.reset()

    din.on_data(on_data)
    din.on_end(on_end)
    din.consume()

def group_by(args, din, dout, raw_args):
    key = args
    handler = Handler(din, emit_on_end="dct")
    def on_data(data):
        value = yutil.get(data, key)

        if value in handler.dct:
            handler.dct[value].append(data)
        else:
            handler.dct[value] = [data]

    din.on_data(on_data)
    din.consume()

def dictify(value):
    if hasattr(value, "_asdict"):
        return dictify(value._asdict())
    elif isinstance(value, dict):
        return {key: dictify(val) for key, val in value.items()}
    elif yutil.is_seq(value):
        return [dictify(item) for item in value]
    else:
        return value

def ps(args, din, dout, raw_args):
    for pid in psutil.get_pid_list():
        try:
            dout.emit(dictify(psutil.Process(pid).as_dict()))
        except psutil._error.NoSuchProcess:
            pass

def net_io(args, din, dout, raw_args):
    for iface, item in psutil.net_io_counters(pernic=True).items():
        data = item._asdict()
        data["name"] = iface
        dout.emit(dictify(data))

def users(args, din, dout, raw_args):
    for item in psutil.get_users():
        dout.emit(dictify(item))

def partitions(args, din, dout, raw_args):
    for partition in psutil.disk_partitions():
        dout.emit(dictify(partition))

def get_uuid(args, din, dout, raw_args):
    dout.emit(dict(uuid=str(uuid.uuid4())))

COMMANDS = {
    "map": cmap,
    "echo": echo,
    "not": cnot,
    "range": crange,
    "is": cis,
    "drop": drop,
    "keep": keep,
    "upper": upper,
    "lower": lower,
    "title": title,
    "capitalize": capitalize,
    "ltrim": ltrim,
    "rtrim": rtrim,
    "trim": trim,
    "split": split,
#    "replace": replace,
    "startswith": startswith,
    "endswith": endswith,
    "all": call,
    "any": cany,
    "bool": cbool,
    "not": cnot,
    "count": count,
    "first": first,
    "last": last,
    "nth": nth,
    "min": cmin,
    "max": cmax,
    "contains": contains,
    "drop-first": drop_first,
    "drop-last": drop_last,
    "keys": keys,
    "values": values,
    "datetime": date_time,
    "timestamp": timestamp,
    "flatten": flatten,
    "sort": sort,
    "shuffle": shuffle,
    "reverse": reverse,
    "set": cset,
    "join": join,
    "collapse": collapse,
    "slice": slice,
    "cat": cat,
    "keep-keys": keep_keys,
    "drop-keys": drop_keys,
    "get": cget,
    "sort-by": sort_by,
    "group-by": group_by,

    "error": error,

    "ls": ls,
    "ps": ps,
    "net-io": net_io,
    "users": users,
    "partitions": partitions,
    "uuid": get_uuid
}
