

from fishhook import Hook
from monomoy.core import db


class User(Hook):
    _obj = {}

    def __init__(self, obj):
        self._obj = obj

    def display_name(self):
        return "%s %s" % (self['first_name'], self['last_name'])

    def __getitem__(self, name):
        if name not in self._obj:
            raise KeyError(name)

        return self._obj[name]


def find_user(spec):
    user = db.users.find_one(spec)
    if user is None:
        return
    return User(user)
