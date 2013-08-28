import collections

def is_int(value, param=None):
    return isinstance(value, int)

def is_float(value, param=None):
    return isinstance(value, float)


def is_number(value, param=None):
    return is_int(value) or is_float(value)

def is_str(value, param=None):
    return isinstance(value, str)

def is_upper(value, param=None):
    return isinstance(value, str) and value.isupper()

def is_lower(value, param=None):
    return isinstance(value, str) and value.islower()

def is_alpha(value, param=None):
    return isinstance(value, str) and value.isalpha()

def is_alnum(value, param=None):
    return isinstance(value, str) and value.isalnum()

def is_space(value, param=None):
    return isinstance(value, str) and value.isspace()

def is_title(value, param=None):
    return isinstance(value, str) and value.istitle()

def is_digit(value, param=None):
    return isinstance(value, str) and value.isdigit()

def is_bool(value, param=None):
    return isinstance(value, bool)

def is_map(data, param=None):
    return isinstance(data, collections.Mapping)

def is_seq(data, param=None):
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

def is_ne(value, param=None):
    return value != param

def is_ge(value, param=None):
    return value >= param

def is_le(value, param=None):
    return value <= param

def is_gt(value, param=None):
    return value > param

def is_lt(value, param=None):
    return value < param

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
    "false?": is_falsy,
    "eq": is_eq,
    "ne": is_ne,
    "gt": is_gt,
    "lt": is_lt,
    "ge": is_ge,
    "le": is_le,
    "upper?": is_upper,
    "lower?": is_lower,
    "alpha?": is_alpha,
    "alnum?": is_alnum,
    "space?": is_space,
    "title?": is_title,
    "digit?": is_digit
}

def __setup():
    items = list(PREDICATES.items())
    for name, predicate in items:
        PREDICATES["not-" + name] = lambda x: not predicate(x)

        if name.endswith("?"):
            PREDICATES["is-" + name[:-1]] = predicate

__setup()

