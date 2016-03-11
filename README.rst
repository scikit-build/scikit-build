===============================
scikit-build
===============================

.. image:: https://badge.fury.io/py/scikit-build.png
    :target: http://badge.fury.io/py/scikit-build

.. image:: https://travis-ci.org/scikit-build/scikit-build.png?branch=master
        :target: https://travis-ci.org/scikit-build/scikit-build

.. image:: https://pypip.in/d/scikit-build/badge.png
        :target: https://pypi.python.org/pypi/scikit-build


Simplify building Python extensions with CMake.  The scikit-build package is
fundamentally just glue between distutils and CMake.  It wraps distutils.setup
so that a CMake build step occurs before calling distutils.setup, and
automatically appends CMake-built output into the distutils package_data as
appropriate.

* Free software: MIT license
* Documentation: http://scikit-build.readthedocs.org.

Features
--------

* (TODO) Wraps distutils so that CMake build step occurs automatically before distutils setup
* (TODO) Passes command line options through to both CMake and distutils (tries to be smart)
* (TODO) Creates simple CMakeLists.txt files for source files that you specify, allowing you to leverage CMake's cross-platform build scripting with less effort.
