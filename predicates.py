import operator

def even(x, arg=None):
    return x % 2 == 0

def odd(x, arg=None):
    return not even(x)

def zero(x, arg=None):
    return x == 0

def empty(x, arg=None):
    return len(x) == 0

def negative(x, arg=None):
    return x < 0

def positive(x, arg=None):
    return x > 0

PREDICATES = {
    "even": even,
    "odd": odd,
    "zero": zero,
    "empty": empty,
    "negative": negative,
    "positive": positive,
    "lt": operator.lt,
    "le": operator.le,
    "eq": operator.eq,
    "ne": operator.ne,
    "ge": operator.ge,
    "gt": operator.gt
}
