#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
from setuptools import setup, find_packages
import os

NAME='rosdevcontroller'
VERSION = '0.1'

install_requires = ['sparts', 'pygobject']
tests_require = []

ROOT = os.path.dirname(__file__)

def read(fpath):
    """Load file contents"""
    with open(os.path.join(ROOT, fpath)) as inf:
        return inf.read()


setup(
    name=NAME,
    version=VERSION,
    packages=find_packages(exclude=['tests', 'tests.*']),
    description="Ros3D device controller",
    long_description=read("README.rst"),
    install_requires=install_requires,
    tests_require=tests_require,
    author='OpenRnD',
    author_email='ros3d@open-rnd.pl',
    license='closed',
    scripts=['ros3d-dev-controller']
)
