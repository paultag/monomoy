monomoy
=======

This tool is used for creating the database for debuild.me
tool. Following are the requirements for this tool.

* pymongo
* flake8
* chardet
* <strike> python-debian </strike>

Initiating debuild.me package DB
--------------------------------

To initiate the debuild.me db run following command. Assuming that
monomoy is not installed system wide.

    MONOMOY_DEVLIB=lib/
    MONOMOY_DEVSHARE=$(pwd)/share
    export MONOMOY_DEVLIB MONOMOY_DEVSHARE
    bin/monomoy init /srv/monomoy
    
This creates basic database required for debuild.me, where packages
can be uploaded.

Installing debuild.me MongoDB database
----------------------------------------

To install the database for debuild.me first you need a preload.json
file with required details. Use the template preload.json in monomoy
source and replace it with required detail. The preload.json itself is
self explanatory about the fields. After creating your version of
preload.json run the following command.

    MONOMOY_DEVLIB=lib/
    MONOMOY_DEVSHARE=$(pwd)/share
    export MONOMOY_DEVLIB MONOMOY_DEVSHARE
    bin/monomoy preload preload.json
    
Uploading package to the debuild.me package DB.
-----------------------------------------------

debuild.me is package source analysis tool so you always need to do a
source only upload to the package DB. This can be achieved using dput.
If you are on local machine you can simply copy source only upload
contents to /srv/monomoy/incoming. You can also use dput tool for
local uploads, for more information check /etc/dput.cf.

Once upload/copy to /srv/monomoy/ you need to run following commands

    cd /srv/monomoy/
    MONOMOY_DEVLIB=/path/to/monomoy/source/lib/
    MONOMOY_DEVSHARE=/path/to/monomoy/source/share
    export MONOMOY_DEVLIB MONOMOY_DEVSHARE
    /path/to/monomoy/source/bin/monomoy process-incoming

If the command exits without any errors you are done. Refresh the
packages page of debuild.me and your package will be listed there






