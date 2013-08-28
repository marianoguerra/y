#!/usr/bin/env python
from __future__ import print_function
import os
import imp
import sys

import edn_format

import yel_utils
from yel_utils import pythonify, run_command, path

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
    status = run_command(name, parsed_options, path, is_map)
    sys.exit(status)

def main():
    name = sys.argv[1]
    args = sys.argv[2:]
    run(name, args)

if __name__ == "__main__":
    main()
