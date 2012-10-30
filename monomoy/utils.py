import os
import time
import json
import datetime
from bson.objectid import ObjectId


def iter_dir(path):
    for f in os.listdir(path):
        yield "%s/%s" % (path, f)


def iter_dir_xtn(path, xtn):
    for f in iter_dir(path):
        if f[-len(xtn):] == xtn:
            yield f


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime.datetime):
            return time.mktime(obj.timetuple())
        return json.JSONEncoder.default(self, obj)
