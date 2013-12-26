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

class TypeChecker(object):
    def get(self, arg):
        return arg

class AnyType(TypeChecker):
    def check(self, args):
        return len(args) == 1

    def get(self, args):
        return args[0]

    def __str__(self):
        return "AnyType"

class OneOfTypes(TypeChecker):
    def __init__(self, *types):
        self.types = types

    def check(self, args):
        return len(args) == 1 and isinstance(args[0], self.types)

    def get(self, args):
        return args[0]

    def __str__(self):
        return "OneOf(%s)" % ", ".join(t.__name__ for t in self.types)

class Maybe(TypeChecker):
    def __init__(self, checker):
        self.checker = checker

    def check(self, args):
        return len(args) == 0 or self.checker.check(args)

    def get(self, args):
        if args:
            return self.checker.get(args)
        else:
            None

    def __str__(self):
        return "Maybe %s" % self.checker

class SeqOf(TypeChecker):
    def __init__(self, *types):
        self.types = types

    def check(self, args):
        return (isinstance(args, collections.Iterable) and
                all(isinstance(arg, self.types) for arg in args))

    def __str__(self):
        return "SeqOf(%s)" % ", ".join(t.__name__ for t in self.types)

Any = AnyType()
Int = OneOfTypes(int)
Float = OneOfTypes(float)
Number = OneOfTypes(int, float)
Bool = OneOfTypes(bool)
StringLike = OneOfTypes(str, yt.Keyword, yt.Symbol)
Str = OneOfTypes(str)
Sym = OneOfTypes(yt.Symbol)
Kw = OneOfTypes(yt.Keyword)

OptInt = Maybe(Int)
OptFloat = Maybe(Float)
OptNumber = Maybe(Number)
OptBool = Maybe(Bool)
OptStringLike = Maybe(StringLike)
OptStr = Maybe(Str)
OptSym = Maybe(Sym)
OptKw = Maybe(Kw)

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
    def fun_command_impl(oin, env, state):
        return (fun(value) for value in oin) 

def col_command(commands, name, fun):
    @commands.command(name=name)
    def fun_command_impl(oin, env, state):
        return force_iter(fun(oin))

def reduce_command(commands, name, fun, initial):
    @commands.command(name=name)
    def fun_command_impl(oin, env, state):
        return functools.reduce(fun, oin, initial)

class Undefined(object):
    pass

__undefined = Undefined()

def is_seq(obj):
    return (not isinstance(obj, str) and
            not isinstance(obj, dict) and
            isinstance(obj, collections.Sequence))

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
