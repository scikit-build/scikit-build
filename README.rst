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


Improved build system generator for CPython C extensions.

Better support is available for additional compilers, build systems, cross
compilation, and locating dependencies and determining their build
requirements. The **scikit-build** package is fundamentally just glue between
the `distutils` Python module and `CMake <https://cmake.org/>`_. Currently,
the package is available to perform builds in a `setup.py` file. In the
future, the project aims to be a build tool option in the `currently
developing pyproject.toml build system specification
<https://www.python.org/dev/peps/pep-0518/>`_.

* Free software: MIT license
* Documentation: http://scikit-build.readthedocs.org
* Source code: https://github.com/scikit-build/scikit-build
* Mailing list: https://groups.google.com/forum/#!forum/scikit-build
