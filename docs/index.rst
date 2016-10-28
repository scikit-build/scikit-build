.. complexity documentation master file, created by
   sphinx-quickstart on Tue Jul  9 22:26:36 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to scikit-build
=======================

**scikit-build** is an improved build system generator for CPython C
extensions. It provides better support for additional compilers, build
systems, cross compilation, and locating dependencies and their associated
build requirements.

The **scikit-build** package is fundamentally just glue between
the `setuptools` Python module and `CMake <https://cmake.org/>`_. Currently,
the package is available to perform builds in a `setup.py` file. In the
future, the project aims to be a build tool option in the `currently
developing pyproject.toml build system specification
<https://www.python.org/dev/peps/pep-0518/>`_.

.. toctree::
   :maxdepth: 2
   :caption: User guide

   installation
   usage
   extension_build_system
   cmake-modules
   contributing
   hacking
   authors
   history

.. toctree::
   :maxdepth: 2
   :caption: For maintainers

   make_a_release

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Resources
=========

* Free software: MIT license
* Documentation: http://scikit-build.readthedocs.io/en/latest/
* Source code: https://github.com/scikit-build/scikit-build
* Mailing list: https://groups.google.com/forum/#!forum/scikit-build
