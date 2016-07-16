===============================
scikit-build
===============================

.. image:: https://badge.fury.io/py/scikit-build.png
    :target: http://badge.fury.io/py/scikit-build

.. image:: https://pypip.in/d/scikit-build/badge.png
    :target: https://pypi.python.org/pypi/scikit-build

.. image:: https://travis-ci.org/scikit-build/scikit-build.png?branch=master
    :target: https://travis-ci.org/scikit-build/scikit-build

.. image:: https://circleci.com/gh/scikit-build/scikit-build/tree/master.svg?style=svg
  :target: https://circleci.com/gh/scikit-build/scikit-build/tree/master

.. image:: https://ci.appveyor.com/api/projects/status/github/scikit-build/scikit-build
    :target: https://ci.appveyor.com/api/projects/status/github/scikit-build/scikit-build


Simplify building Python extensions with CMake.  The scikit-build package is
fundamentally just glue between distutils and CMake.  It wraps
:code:`distutils.setup()` so that a CMake build step occurs before calling
:code:`distutils.setup()`, and automatically appends CMake-built output into the
call arguments as appropriate.

* Free software: MIT license
* Documentation: http://scikit-build.readthedocs.org.

Features
--------

* Wraps distutils so that a CMake build step occurs automatically before
  distutils setup.

* Passes command line options through to both CMake and distutils (tries to be
  smart)

* Uses information extracted from the CMake build to automatically provide most
  of the arguments to :code:`setup()`.

