import os
import pwd
import grp
import datetime

import edn

class Char(str):
    def __new__(cls, value):
        return str.__new__(cls, value)

    def __repr__(self):
        return '<char %s>' % str.__repr__(self)

class Symbol(str):
    def __new__(cls, value):
        return str.__new__(cls, value)

    def __repr__(self):
        return '<symbol %s>' % str.__repr__(self)

class Keyword(str):
    def __new__(cls, value):
        return str.__new__(cls, value)

    def __init__(self, value):
        self.name = value

    def __repr__(self):
        return '<keyword %s>' % str.__repr__(self)

    def __str__(self):
        return ':%s' % str.__str__(self)

class Vector(list):
    def __repr__(self):
        return "<vector %s>" % list.__repr__(self)

TYPES = {
    "char": Char,
    "symbol": Symbol,
    "keyword": Keyword,
    "vector": Vector,
    "list": list,
    "string": str,
    "int": int,
    "float": float,
    "bool": bool
}

class Tagged(object):
    def __init__(self, tag, value):
        self._tag = tag
        self._value = value

    def __str__(self):
        return "#{} {}".format(self._tag, str(self._value))

    def __repr__(self):
        return "<tagged {} {}>".format(self._tag, str(self._value))

NL = Char('\n')
TAB = Char('\t')
RETURN = Char('\r')
SPACE = Char(' ')

class IntTag(int):
    def __new__(self, value):
        return int.__new__(self, value)

    def to_edn(self):
        return Tagged(self.TAG_NAME, int(self))

class FloatTag(float):
    def __new__(self, value):
        return float.__new__(self, value)

    def to_edn(self):
        return Tagged(self.TAG_NAME, float(self))

class StrTag(str):
    def __new__(self, value):
        return str.__new__(self, value)

    def to_edn(self):
        return Tagged(self.TAG_NAME, str(self))

class DictTag(dict):
    def __init__(self, attrs):
        dict.__init__(self, attrs)
        self.__dict__ = attrs

    def to_edn(self):
        return Tagged(self.TAG_NAME, self.__dict__)

# -- common types here
class DateTime(DictTag):
    TAG_NAME = "y.DateTime"
    @classmethod
    def now(cls):
        now = datetime.datetime.now()
        return cls(year=now.year, month=now.month, day=now.day, hour=now.hour,
                minute=now.minute, second=now.second)

CACHED_USER_NAMES  = {}
CACHED_GROUP_NAMES = {}

def get_user_from_uid(uid):
    if uid in CACHED_USER_NAMES:
        return CACHED_USER_NAMES[uid]
    else:
        try:
            username = pwd.getpwuid(uid)[0]
        except KeyError:
            return str(uid)

        CACHED_USER_NAMES[uid] = username
        return username

def get_group_from_gid(gid):
    if gid in CACHED_GROUP_NAMES:
        return CACHED_GROUP_NAMES[gid]
    else:
        try:
            groupname = grp.getgrgid(gid)[0]
        except KeyError:
            return str(gid)

        CACHED_GROUP_NAMES[gid] = groupname
        return groupname

class FileSize(IntTag):
    TAG_NAME = "FileSize"

    def to_human(self):
        return "{} KBs".format(self / 1024)
    
class Uid(IntTag):
    TAG_NAME = "Uid"

    def to_human(self):
        return get_user_from_uid(self)
    
class Gid(IntTag):
    TAG_NAME = "Gid"

    def to_human(self):
        return get_group_from_gid(self)

class Path(StrTag):
    TAG_NAME = "Path"
    
class UnixPerms(IntTag):
    TAG_NAME = "UnixPerms"

class Timestamp(FloatTag):
    TAG_NAME = "Timestamp"

    def to_human(self):
        dtime = datetime.datetime.fromtimestamp(self)
        return dtime.strftime("%c")

class FileType(StrTag):
    TAG_NAME = "FileType"
    TO_HUMAN = {
        "f": "File",
        "d": "Dir",
        "l": "Link",
        "m": "Mount"
    }

    def to_human(self):
        return self.TO_HUMAN.get(self, "Unknwon")

class File(DictTag):
    TAG_NAME = "File"

    @classmethod
    def from_path(cls, fpath):
        stat = os.stat(fpath)
        size = FileSize(stat.st_size)
        uid = Uid(stat.st_uid)
        gid = Gid(stat.st_gid)
        atime = Timestamp(stat.st_atime)
        mtime = Timestamp(stat.st_mtime)
        mode = UnixPerms(stat.st_mode)
        path = Path(os.path.abspath(fpath))

        if os.path.isfile(fpath):
            ftype = "f"
        elif os.path.isdir(fpath):
            ftype = "d"
        elif os.path.islink(fpath):
            ftype = "l"
        elif os.path.ismount(fpath):
            ftype = "m"
        else:
            ftype = "?"

        file_type = FileType(ftype)

        return cls(dict(path=path, size=size, uid=uid, gid=gid, atime=atime,
            mtime=mtime, mode=mode, type=file_type))


EDN_TYPES = {
    "FileSize": FileSize,
    "Uid": Uid,
    "Gid": Gid,
    "Path": Path,
    "UnixPerms": UnixPerms,
    "Timestamp": Timestamp,
    "FileType": FileType,
    "File": File,
    "DateTime": DateTime,
}
