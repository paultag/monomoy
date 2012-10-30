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


def run_command(command):
    """
    Run a synchronized command. The argument must be a list of arguments.
    Returns a triple (stdout, stderr, exit_status)

    If there was a problem to start the supplied command, (None, None, -1) is
    returned
    """
    if not isinstance(command, list):
        command = shlex.split(command)
    try:
        pipe = subprocess.Popen(command,
                                shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    except OSError as e:
        logger.error("Could not execute %s: %s" % (" ".join(command), e))
        return (None, None, -1)
    (output, stderr) = pipe.communicate()
    #if pipe.returncode != 0:
    #   error("Command %s returned failure: %s" % (" ".join(command), stderr))
    return (output, stderr, pipe.returncode)


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime.datetime):
            return time.mktime(obj.timetuple())
        return json.JSONEncoder.default(self, obj)
