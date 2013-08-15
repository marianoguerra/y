#!/usr/bin/env python
from __future__ import print_function
import os
import imp
import sys

import edn_format

import yel_utils
from yel_status import NOT_FOUND
from yel_utils import pythonify, Options, error, LineMapper, next_data, is_seq

path = [os.path.join(os.path.dirname(__file__), 'commands')]

def import_command(name):
    file_, pathname, description = imp.find_module(name, path)
    module = imp.load_module(name, file_, pathname, description)
    file_.close()
    return module

def run(name, command_args):

    if name == "map":
        is_map = True
        name = command_args[0]
        args = command_args[1:]
    else:
        is_map = False
        args = command_args

    if len(args) == 0:
        options_str = "{}"
    elif args[0][0] in ("[", "(") and args[-1][-1] in ("]", ")"):
        options_str = " ".join(args)
    elif args[0][0:2] == "#{" and args[-1][-1] == "}":
        options_str = " ".join(args)
    elif len(args) == 1:
        options_str = args[0]
    else:
        options_str = "{%s}" % " ".join(args)

    parsed_options = pythonify(edn_format.loads(options_str))

    try:
        command = import_command(name)
        default_param = getattr(command, "DEFAULT_PARAM", "value")

        if isinstance(parsed_options, dict):
            dict_options = parsed_options 
            wrapped = False
        else:
            dict_options = {default_param: parsed_options}
            wrapped = True

        options = Options(dict_options, wrapped)
        dout = sys.stdout

        if is_map:
            real_end_unit = yel_utils.END_UNIT
            yel_utils.END_UNIT = " "

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
        else:
            din = sys
        status = command.run(options, din, dout)
        dout.flush()
        sys.exit(status)
    except ImportError:
        error("Command {} not found".format(name), NOT_FOUND)

def main():
    name = sys.argv[1]
    args = sys.argv[2:]
    run(name, args)

if __name__ == "__main__":
    main()
