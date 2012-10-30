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

from monomoy.core import db
from monomoy.errors import MonomoyError
from monomoy.changes import ChangesFileException

from fishhook import Hook


class MonomoyArchiveErrror(MonomoyError):
    pass


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
        if not os.path.exists(root):
            raise MonomoyArchiveErrror("No such folder %s" % (root))
        self._root = root
        self.fire('monomoy-init', {'root': root})

    def _reject_package(self, changes, reason):
        self.fire('monomoy-reject', {
            'srcpkg': changes.get_package_name(),
            'reason': reason
        })

    def _accept_package(self, changes):
        self.fire('monomoy-accept', {
            'changes': changes
        })

    def process_incoming_package(self, changes):
        """
        """
        # firstly, let's check the upload was intact.
        try:
            changes.validate_checksums(check_hash='sha1')
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
        # look up key_id, ensure user is rockn'.
