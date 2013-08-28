from __future__ import print_function

import re
import ast

from rply import ParserGenerator, LexerGenerator
from rply.token import BaseBox

lg = LexerGenerator()

lg.add("boolean", r"(true|false)")
lg.add("nil", r"nil")
lg.add("float", r"\d+\.\d+")
lg.add("number", r"\d+")
lg.add("olist", r"\(")
lg.add("clist", r"\)")
lg.add("omap", r"{")
lg.add("cmap", r"}")
lg.add("ovec", r"\[")
lg.add("cvec", r"\]")
lg.add("sharp", r"#")
lg.add("colon", r":")
lg.add("char_nl", r"\\newline")
lg.add("char_tab", r"\\tab")
lg.add("char_return", r"\\return")
lg.add("char_space", r"\\space")
lg.add("char", r"\\.")
lg.add("symbol", r"[\.\*\+\!\-\_\?\$%&=a-zA-Z][\.\*\+\!\-\_\?\$%&=a-zA-Z0-9:#]*")
lg.add("string", r'"(\\\^.|\\.|[^\"])*"')

lg.ignore(r"[\s,\n]+")
lg.ignore(r";.*\n")

lexer = lg.build()

def show_lex(code):
    tokens = lexer.lex(code)
    token = tokens.next()

    while token is not None:
        print(token.name, token.value)
        token = tokens.next()

pg = ParserGenerator(["boolean", "nil", "float", "number", "olist", "clist",
"omap", "cmap", "ovec", "cvec", "sharp", "colon", "char_nl",
"char_tab", "char_return", "char_space", "char", "symbol", "string"])

class Char(object):
    def __init__(self, value):
        self.__value = value

    def __str__(self):
        return self.__value

    def __repr__(self):
        return '<char "%s">' % self.__value

class Symbol(object):
    def __init__(self, value):
        self.__value = value

    def __str__(self):
        return self.__value

    def __repr__(self):
        return '<symbol "%s">' % self.__value

class Keyword(object):
    def __init__(self, value):
        self.__value = value

    def __str__(self):
        return ":" + self.__value

    def __repr__(self):
        return '<keyword "%s">' % self.__value

class Vector(list):
    def __repr__(self):
        return "<vector %s>" % list.__repr__(self)

class State(object):
    def __init__(self):
        self.level = 0

    def enter(self):
        self.level += 1

    def leave(self):
        self.level -= 1

class Tagged(object):
    def __init__(self, tag, value):
        self.tag = tag
        self.value = value

    def __str__(self):
        return "#{} {}".format(self.tag, str(self.value))

    def __repr__(self):
        return "<tagged {} {}>".format(self.tag, str(self.value))

NL = Char('\n')
TAB = Char('\t')
RETURN = Char('\r')
SPACE = Char(' ')

@pg.production("main : value")
def main(state, p):
    return p[0]

@pg.production("items : value")
def value_items_one(state, p):
    return [p[0]]

@pg.production("pairs : value value pairs")
def value_pairs(state, p):
    return [(p[0], p[1])] + p[2]

@pg.production("pairs : value value")
def value_pairs_one(state, p):
    return [(p[0], p[1])]

@pg.production("items : value items")
def value_items_more(state, p):
    return [p[0]] + p[1]

@pg.production("value : sharp omap cmap")
def value_empty_set(state, p):
    return set()

@pg.production("value : omap cmap")
def value_empty_map(state, p):
    return {}

@pg.production("value : omap pairs cmap")
def value_map(state, p):
    return dict(p[1])

@pg.production("value : ovec cvec")
def value_empty_vec(state, p):
    return Vector()

@pg.production("value : olist clist")
def value_empty_list(state, p):
    return []

@pg.production("value : sharp omap items cmap")
def value_set(state, p):
    return set(p[2])

@pg.production("value : ovec items cvec")
def value_vec(state, p):
    return Vector(p[1])

@pg.production("value : olist items clist")
def value_list(state, p):
    return p[1]

@pg.production("value : number")
def value_integer(state, p):
    return int(p[0].value)

@pg.production("value : float")
def value_float(state, p):
    return float(p[0].value)

@pg.production("value : nil")
def value_nil(state, p):
    return None

@pg.production("value : boolean")
def value_boolean(state, p):
    return p[0].value == "true"

@pg.production("value : char_nl")
def value_char_nl(state, p):
    return NL

@pg.production("value : char_tab")
def value_char_tab(state, p):
    return TAB

@pg.production("value : char_return")
def value_char_return(state, p):
    return RETURN

@pg.production("value : char_space")
def value_char_space(state, p):
    return SPACE

@pg.production("value : char")
def value_char(state, p):
    return Char(p[0].value[1])

@pg.production("value : string")
def value_string(state, p):
    return ast.literal_eval(p[0].value)

@pg.production("value : symbol")
def value_symbol(state, p):
    return Symbol(p[0].value)

@pg.production("value : colon symbol")
def value_keyword(state, p):
    return Keyword(p[1].value)

parser = pg.build()

def loads(code):
    state = State()
    return parser.parse(lexer.lex(code), state)

CHARS = {
    '\t': 'tab',
    '\n': 'newline',
    '\r': 'return',
    ' ': 'space'
}

ESCAPE = re.compile(r'[\x00-\x1f\\"\b\f\n\r\t]')
ESCAPE_DCT = {
    '\\': '\\\\',
    '"': '\\"',
    '\b': '\\b',
    '\f': '\\f',
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t',
}

for i in range(0x20):
    ESCAPE_DCT.setdefault(chr(i), '\\u{0:04x}'.format(i))

def encode_basestring(s):
    """Return a edn representation of a Python string"""
    def replace(match):
        return ESCAPE_DCT[match.group(0)]

    return '"' + ESCAPE.sub(replace, s) + '"'

def dumps(obj):
    if isinstance(obj, Vector):
        return "[%s]" % " ".join([dumps(item) for item in obj])
    elif isinstance(obj, Tagged):
        return "#{} {}".format(obj.tag, dumps(obj.value))
    elif isinstance(obj, list):
        return "(%s)" % " ".join([dumps(item) for item in obj])
    elif isinstance(obj, dict):
        keyvals = " ".join([" ".join([dumps(k), dumps(v)]) for k, v in obj.items()])
        return "{%s}" % keyvals
    elif isinstance(obj, Char):
        val = str(obj)
        return "\\%s" % CHARS.get(val, val)
    elif isinstance(obj, Keyword):
        return str(obj)
    elif isinstance(obj, Symbol):
        return str(obj)
    elif obj is True:
        return "true"
    elif obj is False:
        return "false"
    elif obj is None:
        return "nil"
    elif isinstance(obj, str):
        return encode_basestring(obj)
    elif isinstance(obj, set):
        return "#{%s}" % " ".join([dumps(item) for item in obj])
    elif isinstance(obj, (int, float)):
        return str(obj)
    else:
        raise ValueError("Unknown value {} of type {}".format(obj, type(obj)))


if __name__ == "__main__":
    #show_lex('{:foo 1 "bar" 1.2 :baz true false nil [1 #{}] (2 []) key #mg.value 42}')
    print(loads("42"))
    print(loads("nil"))
    print(loads("true"))
    print(loads("false"))
    print(loads("1.2"))
    print(repr(loads(r"\tab")))
    print(repr(loads(r"\newline")))
    print(repr(loads(r"\return")))
    print(repr(loads(r"\space")))
    print(repr(loads(r"\s")))
    print(loads('"a string"'))
    print(repr(loads("symbol")))
    print(repr(loads(":keyword")))
    print(repr(loads("#{}")))
    print(repr(loads("#{1}")))
    print(repr(loads("#{1 2}")))
    print(repr(loads("{}")))
    print(repr(loads("[]")))
    print(repr(loads("[1]")))
    print(repr(loads("()")))
    print(repr(loads("([] () {} #{})")))
    print(repr(loads("(1)")))
    print(repr(loads("(1 true nil)")))
    print(repr(loads("{:foo 42}")))
    print(repr(loads("{:foo 42 bar true \\a 12.3}")))

    print()

    print(dumps("asd"))
    print(dumps(loads(r'"a\"sd"')))
    print(dumps(loads("(1 true nil [1.2 {:foo 42 bar true \\a 12.3 \"asd\" \\newline}])")))
    print(dumps(Tagged("y.Error", loads('{:reason "asd" :status 500}'))))
