import os
import pwd
import grp
import datetime

import edn
from edn import Tagged

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

class FileSize(Tagged):
    
    def __init__(self, value):
        Tagged.__init__(self, "y.FileSize", value)

    def to_human(self):
        return "{} KBs".format(self.value / 1024)

class Uid(Tagged):
    
    def __init__(self, value):
        Tagged.__init__(self, "y.Uid", value)

    def to_human(self):
        return get_user_from_uid(self.value)

class Gid(Tagged):
    
    def __init__(self, value):
        Tagged.__init__(self, "y.Gid", value)

    def to_human(self):
        return get_group_from_gid(self.value)

class Path(Tagged):
    
    def __init__(self, value):
        Tagged.__init__(self, "y.Path", value)

class UnixPerms(Tagged):
    def __init__(self, value):
        Tagged.__init__(self, "y.UnixPerms", value)

class Timestamp(Tagged):

    def __init__(self, value):
        Tagged.__init__(self, "y.Timestamp", value)

    def to_human(self):
        dtime = datetime.datetime.fromtimestamp(self.value)
        return dtime.strftime("%c")


class FileType(Tagged):
    TO_HUMAN = {
        "f": "File",
        "d": "Dir",
        "l": "Link",
        "m": "Mount"
    }

    def __init__(self, value):
        Tagged.__init__(self, "y.FileType", value)

    def to_human(self):
        return self.TO_HUMAN.get(self.value, "Unknwon")

class File(dict, Tagged):

    def __init__(self, value):
        Tagged.__init__(self, "y.File", value)

    @classmethod
    def from_path(cls, fpath):
        stat = os.stat(fpath)
        size = FileSize(stat.st_size)
        uid = Uid(stat.st_uid)
        gid = Gid(stat.st_gid)
        atime = Timestamp(stat.st_atime)
        mtime = Timestamp(stat.st_mtime)
        mode = UnixPerms(oct(stat.st_mode))
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
