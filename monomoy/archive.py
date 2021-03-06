# Copyright (c) 2012 Paul Tagliamonte <paultag@debian.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import os
import shutil
import datetime as dt
from bson.objectid import ObjectId

from monomoy.core import db
from monomoy.errors import MonomoyError
from monomoy.changes import ChangesFileException

from fishhook import Hook


class MonomoyArchiveErrror(MonomoyError):
    pass


def _get_archive_path(objid):
    path = ""
    nests = 4
    for n in range(0, nests):
        path += objid[n] + "/"
    path += objid
    return path


class MonomoyArchive(Hook):
    """
    Internal archive implementation. This helps to abstract away some of
    the pain in dealing with the archive.

    This isn't an apt repo.
    """

    def __init__(self, root):
        """
        Initalize the repo & all that. May raise a MonomoyArchiveErrror
        if the ``root`` does not exist.
        """
        root = os.path.abspath(root)
        if not os.path.exists(root):
            raise MonomoyArchiveErrror("No such folder %s" % (root))
        self._root = root

    def _reject_package(self, changes, reason):
        """
        """
        self.fire('monomoy-package-rejected', {
            'srcpkg': changes.get_package_name(),
            'changes': changes,
            'reason': reason
        })
        for fd in changes.get_files():
            os.unlink(fd)
        os.unlink(changes.get_changes_file())

    def _accept_package(self, changes, user):
        """
        """
        processed_changes = changes._get_changes_obj()
        processed_dsc = changes._get_dsc_obj()

        package_id = db.packages.insert({
            "name": changes.get_package_name(),
            "version": changes.get("Version"),
            "changes": processed_changes,
            "dsc": processed_dsc,
            "user": user['_id'],
            "accepted_at": dt.datetime.now()
        })

        self.fire('monomoy-package-accepted', {
            'package': package_id,
            'changes': changes,
            'user': user
        })

        folder = "%s/%s" % (self._root, _get_archive_path(str(package_id)))
        os.makedirs(folder)
        for fd in changes.get_files():
            shutil.move(fd, folder)
        os.unlink(changes.get_changes_file())

    def process_incoming_package(self, changes):
        """
        """
        # firstly, let's check the upload was intact.
        try:
            changes.validate_checksums(check_hash='sha1')
        except IOError:
            # Partial uploads should push .changes last.
            self.fire('monomoy-package-incomplete', {
                'changes': changes
            })
            os.unlink(changes.get_changes_file())
        except ChangesFileException:
            self._reject_package(
                changes,
                "Checksums are invalid."
            )
            return

        try:
            key_id = changes.validate_signature()
        except ChangesFileException:
            self._reject_package(
                changes,
                "Signature is invalid."
            )
            return

        user = db.users.find_one({
            "gpg": key_id
        })
        if user is None:
            self._reject_package(
                changes,
                "No such user."
            )
            return

        self._accept_package(changes, user)

    def get_package(self, objid):
        """
        """
        obj = objid
        if isinstance(objid, str):
            obj = ObjectId(objid)
        results = db.packages.find_one({"_id": obj})
        return results

    def get_packages(self):
        """
        """
        spec = {}  # dynamic searching?
        return db.packages.find(spec)

    def get_package_root(self, pkg_id):
        """
        """
        pkg = self.get_package(pkg_id)
        if pkg is None:
            return  # XXX: Exception.
        return _get_archive_path(str(pkg['_id']))

    def remove_package(self, objid):
        """
        """
        pkg = self.get_package(objid)
        if pkg is None:
            return
        path = "%s/%s" % (self._root, _get_archive_path(str(pkg['_id'])))
        shutil.rmtree(path)
        for job in db.jobs.find({"package": pkg['_id']}):
            db.checks.remove({"job": job['_id']}, safe=True)
            db.jobs.remove({"_id": job['_id']}, safe=True)

        db.packages.remove({
            "_id": pkg['_id']
        }, safe=True)
        self.fire('monomoy-package-removed', {
            "package": pkg,
            "path": path
        })
