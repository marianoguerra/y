import collections

def is_int(value, param=None):
    return isinstance(value, int)

def is_float(value, param=None):
    return isinstance(value, float)


def is_number(value, param=None):
    return is_int(value) or is_float(value)

def is_str(value, param=None):
    return isinstance(value, str)

def is_bool(value, param=None):
    return isinstance(value, bool)

def is_map(data):
    return isinstance(data, collections.Mapping)

def is_seq(data):
    return isinstance(data, collections.Iterable) and not isinstance(data, str)

def is_sized(value, param=None):
    return isinstance(value, collections.Sized)

def is_empty(value, param=None):
    return is_sized(value) and len(value) == 0

def is_zero(value, param=None):
    return value == 0 or value == 0.0

def is_even(value, param=None):
    return is_number(value) and value % 2 == 0

def is_odd(value, param=None):
    return is_number(value) and not is_even(value)

def is_nil(value, param=None):
    return value is None

def is_not_nil(value, param=None):
    return value is not None

def is_eq(value, param=None):
    return value == param

def is_truthy(value, param=None):
    return bool(value)

def is_falsy(value, param=None):
    return not bool(value)

PREDICATES = {
    "nil?": is_nil,
    "int?": is_int,
    "float?": is_float,
    "number?": is_number,
    "str?": is_str,
    "bool?": is_bool,
    "map?": is_map,
    "seq?": is_seq,
    "sized?": is_sized,
    "empty?": is_empty,
    "zero?": is_zero,
    "even?": is_even,
    "odd?": is_odd,
    "eq?": is_eq,
    "true?": is_truthy,
    "false?": is_falsy
}

for name, predicate in PREDICATES.items():
    PREDICATES["not-" + name] = lambda x: not predicate(x)
