===============================
scikit-build
===============================

.. image:: https://img.shields.io/pypi/v/scikit-build.svg?maxAge=2592000
    :target: https://pypi.python.org/pypi/scikit-build

.. image:: https://img.shields.io/pypi/dm/scikit-build.svg?maxAge=2592000
    :target: https://pypi.python.org/pypi/scikit-build

.. image:: https://requires.io/github/scikit-build/scikit-build/requirements.svg?branch=master
     :target: https://requires.io/github/scikit-build/scikit-build/requirements/?branch=master
     :alt: Requirements Status

.. image:: https://img.shields.io/travis/scikit-build/scikit-build.svg?maxAge=2592000
    :target: https://travis-ci.org/scikit-build/scikit-build

.. image:: https://ci.appveyor.com/api/projects/status/77bjtsihsjaywjr0?svg=true
    :target: https://ci.appveyor.com/project/scikit-build/scikit-build/branch/master

.. image:: https://circleci.com/gh/scikit-build/scikit-build/tree/master.svg?style=svg
    :target: https://circleci.com/gh/scikit-build/scikit-build/tree/master

.. image:: https://codecov.io/gh/scikit-build/scikit-build/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/scikit-build/scikit-build

.. image:: https://landscape.io/github/scikit-build/scikit-build/document-api/landscape.svg?style=flat
   :target: https://landscape.io/github/scikit-build/scikit-build/document-api
   :alt: Code Health

Improved build system generator for CPython C extensions.

Better support is available for additional compilers, build systems, cross
compilation, and locating dependencies and determining their build
requirements. The **scikit-build** package is fundamentally just glue between
the `setuptools` Python module and `CMake <https://cmake.org/>`_. Currently,
the package is available to perform builds in a `setup.py` file. In the
future, the project aims to be a build tool option in the `currently
developing pyproject.toml build system specification
<https://www.python.org/dev/peps/pep-0518/>`_.

* Free software: MIT license
* Documentation: http://scikit-build.readthedocs.org
* Source code: https://github.com/scikit-build/scikit-build
* Mailing list: https://groups.google.com/forum/#!forum/scikit-build
