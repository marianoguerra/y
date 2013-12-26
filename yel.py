#!/usr/bin/env python3
import edn
import sys
import yutil
import ytypes as yt
import itertools
import commands
import str_commands
import ps_commands

def edn_to_obj(edn_iter, env):
    for edn_text in edn_iter:
        yield env.from_edn(edn_text)

def run_command(command, env, args, kwargs, objs_in):
    state = yutil.build_state(command)
    for obj_out in command(objs_in, env, state, *args, **kwargs):
        yield obj_out

def run_command_edn_in(command, env, args, kwargs, edn_iter):
    objs_in = edn_to_obj(edn_iter, env)
    return run_command(command, env, args, kwargs, objs_in)

def run_command_edn_in_out(command, env, args, kwargs, edn_iter=sys.stdin):
    for result in run_command_edn_in(command, env, args, kwargs, edn_iter):
        yield edn.dumps(result)

def is_keyword(obj):
    return isinstance(obj, yt.Keyword)

def isnt_keyword(obj):
    return not is_keyword(obj)

def get_until_keyword(iterable):
    return itertools.takewhile(isnt_keyword, iterable)

def parse_args(args_str, env):
    args = [env.from_edn(arg) for arg in args_str]
    rargs = list(get_until_keyword(args))
    kwargs_iter = args[len(rargs):]
    kwargs = {}

    accum = None
    current_key = None
    for obj in kwargs_iter:
        if is_keyword(obj):
            if current_key is not None:
                kwargs[current_key.name] = accum or [True]

            accum = []
            current_key = obj
        else:
            accum.append(obj)

    if current_key:
        kwargs[current_key.name] = accum or [True]

    return rargs, kwargs

def main(command_name, args):
    env = yutil.Env(commands.COMMANDS.commands)
    env.add_namespace("str", str_commands.COMMANDS.commands)
    # TODO: import
    env.add_namespace("ps", ps_commands.COMMANDS.commands)
    command = env.resolve(command_name)

    if callable(command):
        args, kwargs = parse_args(args, env)
        for result in run_command_edn_in_out(command, env, args, kwargs):
            print(result)
    else:
        # TODO: yield y.Error
        print("ERROR: command %s not found" % command_name)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
