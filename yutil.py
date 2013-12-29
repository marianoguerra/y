import edn
import inspect
import itertools
import functools
import collections
import predicates
import ytypes as yt

def default_state_builder():
    return {}

def build_state(command):
    initial_state_builder = getattr(command, "initial_state_builder",
                                                        default_state_builder)
    return initial_state_builder()

class Env(object):
    def __init__(self, bindings=None):
        self.bindings = bindings if bindings is not None else {}
        self.types = yt.TYPES.copy()
        self.predicates = {}
        self.edn_types = yt.EDN_TYPES.copy()

        for key, val in yt.TYPES.items():
            self.predicates[key] = val

        for key, val in predicates.PREDICATES.items():
            self.predicates[key] = val

    def to_human(self, obj, mode=None):
        to_human = getattr(obj, "to_human", None)
        if to_human:
            return to_human(mode)
        elif is_seq(obj):
            return "\t".join(self.to_human(o, mode) for o in obj)
        elif is_map(obj):
            return {key: self.to_human(o, mode) for key, o in obj.items()}
        else:
            return obj


    def add_namespace(self, ns_name, values):
        self.bindings[ns_name] = values

    def is_type(self, value, type_name):
        type_ = self.types.get(type_name)
        if type_:
            return isinstance(value, type_)
        else:
            return False

    def check_predicate(self, value, pred_name, arg=None):
        predicate = self.predicates.get(pred_name)
        if predicate:
            return predicate(value, arg)
        else:
            return False

    def from_edn(self, edn_value):
        return edn.loads(edn_value, self.edn_types)

    def to_edn(self, value):
        return edn.dumps(value)

    def resolve(self, name):
        tokens = name.split("/", 1)

        if len(tokens) == 2:
            ns, symbol = tokens
            result = self.bindings.get(ns, {}).get(symbol)
        else:
            result = self.bindings.get(name)

        return result


class Commands(object):
    def __init__(self):
        self.commands = {}

    def command(self, name=None):
        def inner(f):
            fname = name or f.__name__
            self.commands[fname] = f
            return f

        return inner

def force_iter(obj):
    if isinstance(obj, collections.Iterable):
        return obj
    else:
        return [obj]

def fun_command(commands, name, fun):
    @commands.command(name=name)
    def fun_command_impl(oin, env):
        return (fun(value) for value in oin) 

def col_command(commands, name, fun):
    @commands.command(name=name)
    def fun_command_impl(oin, env):
        yield from force_iter(fun(oin))

def reduce_command(commands, name, fun, initial):
    @commands.command(name=name)
    def fun_command_impl(oin, env):
        return functools.reduce(fun, oin, initial)

def tap(fun):
    def do(data):
        fun(data)
        return data
    return do

class Undefined(object):
    pass

__undefined = Undefined()

def is_seq(obj):
    return (not isinstance(obj, str) and
            not isinstance(obj, dict) and
            isinstance(obj, collections.Sequence))

def is_map(obj):
    return isinstance(obj, collections.Mapping)

def get_key(obj, name, default=None):
    if obj is None:
        return default

    elif isinstance(obj, collections.Mapping):
        return obj.get(name, default)
    elif isinstance(obj, collections.Sequence):
        if isinstance(name, int) and len(obj) > name:
            return obj[name]
        else:
            return default
    elif isinstance(name, str) and hasattr(obj, name):
        return getattr(obj, name, default)
    else:
        return default

def get_path(obj, names, default=None):
    current = obj
    for name in names:
        current = get_key(current, name, __undefined)
        if current is __undefined:
            return default
        elif current is None:
            return current

    return current

class Type(object):
    pass

class OneOf(Type):
    def __init__(self, *types):
        self.types = types

class SeqOf(Type):
    def __init__(self, *types):
        self.types = types

class Maybe(Type):
    def __init__(self, type):
        self.type = type

class AnyType(Type):
    pass

EdnStrLike = OneOf(str, yt.Symbol, yt.Keyword)
Any = AnyType()
