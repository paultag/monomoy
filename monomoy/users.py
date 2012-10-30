

from fishhook import Hook
from monomoy.core import db


class User(Hook):
    def __init__(self, obj):
        self._obj = obj

    def display_name(self):
        return "%s %s" % (self._obj['first_name'], self._obj['last_name'])


def find_user(spec):
    user = db.users.find_one(spec)
    if user is None:
        return
    return User(user)
