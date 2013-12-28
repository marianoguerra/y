import os
import random
import operator
import datetime

import edn
from yutil import *
import ytypes as yt
COMMANDS = Commands()

fun_command(COMMANDS, "to-edn", edn.dumps)
fun_command(COMMANDS, "to-bool", bool)
fun_command(COMMANDS, "not", lambda x: not bool(x))
fun_command(COMMANDS, "identity", lambda x: x)
fun_command(COMMANDS, "reverse", lambda x: x[::-1])

fun_command(COMMANDS, "keys", operator.methodcaller("keys"))
fun_command(COMMANDS, "values", operator.methodcaller("values"))
fun_command(COMMANDS, "items", operator.methodcaller("items"))

col_command(COMMANDS, "size", lambda x: len(list(force_iter(x))))
col_command(COMMANDS, "list", lambda x: [list(x)])
col_command(COMMANDS, "any", any)
col_command(COMMANDS, "all", all)
col_command(COMMANDS, "max", max)
col_command(COMMANDS, "min", min)

@COMMANDS.command()
def shuffle(oin, env, state):
    items = list(force_iter(oin))
    random.shuffle(items)
    yield from items

@COMMANDS.command()
def sort(oin, env, state):
    items = list(force_iter(oin))
    yield from sorted(items)

# TODO
@COMMANDS.command("group-by")
def group_by(oin, env, state, *names):
    result = {}
    for obj in oin:
        key = get_path(obj, names)
        result[key] = obj

    yield result

@COMMANDS.command("to-set")
def cset(oin, env, state):
    yield from set(force_iter(oin))

@COMMANDS.command("from-edn")
def from_edn(oin, env, state):
    return (env.from_edn(obj) for obj in oin)

reduce_command(COMMANDS, "add", operator.add, 0)
reduce_command(COMMANDS, "sub", operator.sub, 0)
reduce_command(COMMANDS, "mul", operator.mul, 1)
reduce_command(COMMANDS, "div", operator.truediv, 1)

@COMMANDS.command("is")
def cis(oin, env, state, pred_name, arg=None):
    """Check if value pass predicate pred_name"""
    return (env.check_predicate(obj, pred_name, arg) for obj in oin)

@COMMANDS.command("isnt")
def cisnt(oin, env, state, pred_name, arg=None):
    """Check if value doesn't pass predicate pred_name"""
    return (not env.check_predicate(obj, pred_name, arg) for obj in oin)

@COMMANDS.command("keep")
def keep(oin, env, state, pred_name, arg=None):
    """keep objects that satisfy predicate"""
    return (obj for obj in oin if env.check_predicate(obj, pred_name, arg))

@COMMANDS.command("drop")
def drop(oin, env, state, pred_name, arg=None):
    """drop objects that satisfy predicate"""
    return (obj for obj in oin if not env.check_predicate(obj, pred_name, arg))

@COMMANDS.command()
def inc(oin, env, state, by=1):
    "Increase input by a given amount (default to 1)"
    return (obj + by for obj in oin)

@COMMANDS.command("flatten1")
def flatten1(oin, env, state):
    for obj in oin:
        for item in force_iter(obj):
            yield item

@COMMANDS.command("get")
def getks(oin, env, state, *names, default=None):
    for obj in oin:
        yield get_path(obj, names, default)

@COMMANDS.command("keep-keys")
def keep_keys(oin, env, state, *names):
    for obj in oin:
        yield {str(key): obj[key] for key in names}

@COMMANDS.command("drop-keys")
def drop_keys(oin, env, state, *names):
    name_set = set(names)
    for obj in oin:
        yield {key: val for key, val in obj.items() if key not in name_set}

@COMMANDS.command("range")
def crange(oin, env, state, start=0, stop=10, step=1):
    return range(start, stop, step)

@COMMANDS.command("now")
def now(oin, env, state):
    yield yt.DateTime.now()

@COMMANDS.command("slice")
def cslice(oin, env, state, start=None, stop=None, step=None):
    getter = operator.itemgetter(slice(start, stop, step))
    for obj in oin:
        yield getter(obj)

@COMMANDS.command("first")
def cfirst(oin, env, state, n=1):
    yield from cslice(oin, env, state, stop=n)

@COMMANDS.command("last")
def clast(oin, env, state, n=1):
    yield from cslice(oin, env, state, start=-n)

@COMMANDS.command("drop-first")
def drop_first(oin, env, state, n=1):
    yield from cslice(oin, env, state, start=n)

@COMMANDS.command("drop-last")
def drop_last(oin, env, state, n=1):
    yield from cslice(oin, env, state, stop=-n)

@COMMANDS.command("eval")
def ceval(oin, env, state, command_name, *args, **kwargs):
    command = env.resolve(command_name)
    if callable(command):
        state = build_state(command)
        yield from command(oin, env, state, *args, **kwargs)
    else:
        raise KeyError("Command %s not found" % command_name)
    
@COMMANDS.command("map")
def cmap(oin, env, state, command_name, *args, **kwargs):
    command = env.resolve(command_name)
    if callable(command):
        for obj in oin:
            state = build_state(command)
            yield command(force_iter(obj), env, state, *args, **kwargs)
    else:
        raise KeyError("Command %s not found" % command_name)
    
@COMMANDS.command("ls")
def ls(oin, env, state, path=".", deep=False):
    if os.path.isdir(path):
        for _dirpath, dirnames, filenames in os.walk(path):

            for dirname in dirnames:
                yield yt.File.from_path(dirname)

            for filename in filenames:
                yield yt.File.from_path(filename)

            if not deep:
                break 

    else:
        yield yt.File.from_path(path)
