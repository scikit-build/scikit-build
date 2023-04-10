.. complexity documentation master file, created by
   sphinx-quickstart on Tue Jul  9 22:26:36 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root ``toctree`` directive.

Welcome to scikit-build
=======================

**scikit-build** is an improved build system generator for CPython C/C++/Fortran/Cython
extensions. It provides better support for additional compilers, build
systems, cross compilation, and locating dependencies and their associated
build requirements.

The **scikit-build** package is fundamentally just glue between
the ``setuptools`` Python module and `CMake <https://cmake.org/>`_.

To get started, see :ref:`this example <basic_usage_example>`.
For more examples, see `scikit-build-sample-projects <https://github.com/scikit-build/scikit-build-sample-projects>`_.

The next generation of scikit-build, `scikit-build-core
<https://scikit-build-core.readthedocs.io>`_, is currently under development.
This provides a simple, reliable PEP 517 based build backend for CMake that does
not use setuptools and provides a lot of new features. Scikit-build-core
can also power a setuptools-based extension system, which will eventually become
the backend for scikit-build (classic). If you do not require extensive
customization of the build process, you should consider trying scikit-build-core
instead of scikit-build.

.. toctree::
   :maxdepth: 2
   :caption: User guide

   installation
   usage
   generators
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
* Discussions: https://github.com/orgs/scikit-build/discussions
