#!/usr/bin/env python

from monomoy import __appname__, __version__
from setuptools import setup

long_description = open('README.md', 'r').read()

setup(
    name=__appname__,
    version=__version__,
    packages=[
        'monomoy'
    ],
    author="Paul Tagliamonte",
    author_email="paultag@debian.org",
    long_description=long_description,
    description='does some stuff with things & stuff',
    license="Expat",
    url="",
    platforms=['any']
)
