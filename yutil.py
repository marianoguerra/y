from __future__ import print_function
import sys
import collections
import logging
logging.basicConfig()
logger = logging.getLogger("y")

from commands import COMMANDS

import edn

def is_seq(obj):
    return (not isinstance(obj, str) and
            not isinstance(obj, dict) and
            isinstance(obj, collections.Iterable))

def is_assoc(obj):
    return isinstance(obj, collections.Mapping)

def to_list(obj):
    return obj if is_seq(obj) else [obj]

def get(obj, key, default=None):
    if is_assoc(obj):
        return obj.get(key, default)
    elif isinstance(obj, collections.Iterable) and key in obj:
        return obj[key]
    else:
        return default

class DataGenerator(object):
    def __init__(self):
        self.callbacks = []
        self.errbacks = []
        self.endbacks = []
        self.startbacks = []
        self._stop = False

    def on_data(self, callback):
        self.callbacks.append(callback)

    def on_error(self, callback):
        self.errbacks.append(callback)

    def on_start(self, callback):
        self.startbacks.append(callback)

    def on_end(self, callback):
        self.endbacks.append(callback)

    def notify_end(self):
        for endback in self.endbacks:
            try:
                endback()
            except Exception as error:
                self.notify_error(error)

    def notify_start(self):
        for startback in self.startbacks:
            try:
                startback()
            except Exception as error:
                self.notify_error(error)

    def notify_error(self, error):
        for errback in self.errbacks:
            try:
                errback(error)
            except Exception as error:
                logger.error("Error notifying errors (?)")
                logger.error(error)
                raise error

    def notify(self, data):
        for callback in self.callbacks:
            try:
                callback(data)
            except Exception as error:
                self.notify_error(error)

    def next(self):
        raise NotImplementedError()

    def consume(self):
        while not self._stop and self.next():
            pass

    def stop(self):
        self._stop = True

    def is_stopped(self):
        return self._stop


class LineReader(DataGenerator):

    def __init__(self, din):
        DataGenerator.__init__(self)
        self.din = din
        self.first = True

    def next(self):
        if self.first:
            self.first = False
            self.notify_start()

        line = self.din.readline()
        if line == "":
            self.notify_end()
            return False
        else:
            self.notify(line)
            return True

class EdnReader(DataGenerator):

    def __init__(self, din):
        DataGenerator.__init__(self)
        self.din = din
        self.din.on_data(self._on_data)
        self.din.on_error(self.notify_error)
        self.din.on_start(self.notify_start)
        self.din.on_end(self.notify_end)

    def _on_data(self, data):
        try:
            edn_data = edn.loads(data)
            self.notify(edn_data)
        except Exception as error:
            self.notify_error(error)

    def next(self):
        return self.din.next()

class Error(edn.Tagged):
    def __init__(self, reason, status):
        edn.Tagged.__init__(self, "y.Error",
                dict(reason=reason, status=status))

class Writer(object):

    def __init__(self, dout, sep="\n"):
        self.sep = sep
        self.dout = dout

    def emit(self, data):
        self.dout.write(data)

    def raw_write(self, data):
        self.dout.write(data)

    def error(self, reason, status=500):
        self.emit(Error(reason, status))

class EdnIterator(DataGenerator):

    def __init__(self, data):
        DataGenerator.__init__(self)
        self.data = data
        self.is_first = True

    def next(self):
        if self.is_first:
            self.notify_start()
            self.is_first = False

        if self._stop:
            is_end = True
        elif is_seq(self.data):
            if self.data:
                self.notify(self.data.pop(0))
                is_end = not self.data
            else:
                is_end = True
        else:
            self.notify(self.data)
            is_end = True

        if is_end:
            self.notify_end()

        return not is_end

    def consume(self):
        while self.next():
            pass


class EdnWriter(Writer):

    def __init__(self, dout, sep="\n", write_sep_after_first=False):
        Writer.__init__(self, dout, sep)
        self.write_sep_after_first = write_sep_after_first
        self.first = True

    def emit(self, data):
        if not self.first and self.write_sep_after_first:
            self.dout.write(self.sep)

        self.dout.write(edn.dumps(data))

        if not self.write_sep_after_first:
            self.dout.write(self.sep)

        # TODO: remove?
        self.dout.flush()

        self.first = False

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
    if isinstance(obj, edn.Symbol):
        return StrSymbol(obj)
    elif isinstance(obj, edn.Keyword):
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

def parse_args(args, first_n_args_raw=0):
    raw_args = args[:first_n_args_raw]
    to_parse = args[first_n_args_raw:]

    if len(to_parse) == 0:
        options_str = "{}"
    elif to_parse[0][0] in ("[", "(") and to_parse[-1][-1] in ("]", ")"):
        options_str = " ".join(to_parse)
    elif to_parse[0][0:2] == "#{" and to_parse[-1][-1] == "}":
        options_str = " ".join(to_parse)
    elif len(to_parse) == 1:
        options_str = to_parse[0]
    else:
        options_str = "{%s}" % " ".join(to_parse)

    parsed = pythonify(edn.loads(options_str))

    return raw_args, parsed

def load_command(name):
    return COMMANDS.get(name, None)

def run_command(name, args, din=None, dout=None):
    din = din if din is not None else sys.stdin
    dout = dout if dout is not None else sys.stdout
    lines = LineReader(din)
    ednin = EdnReader(lines)
    ednout = EdnWriter(dout)

    def on_error(error):
        ednout.error(str(error), 500)

    ednin.on_error(on_error) 
    lines.on_error(on_error)

    command = load_command(name)

    if command:
        if getattr(command, "keep_args_raw", False):
            command(args, ednin, ednout, None)
        else:
            raw_args, parsed = parse_args(args,
                    getattr(command, "n_raw_args", 0))
            command(parsed, ednin, ednout, raw_args)
    else:
        print("Error: command '{}' not found".format(name))
