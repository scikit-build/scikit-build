#!/usr/bin/env python
from __future__ import print_function
from pycmake.distutils_wrap import setup

PKG = "test1"
version = "0.1.0"

setup(
    name=PKG,
    version=version,
    description="The {0} package".format(PKG),
    author='PyCMake team',
    license="MIT",
    zip_safe=False,
    test_suite='tests',
    packages=["test1"],
)
