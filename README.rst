===============================
scikit-build
===============================

.. image:: https://github.com/scikit-build/scikit-build/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/scikit-build/scikit-build/actions/workflows/ci.yml

.. image:: https://dev.azure.com/scikit-build/scikit-build/_apis/build/status/scikit-build.scikit-build?branchName=master
   :target: https://dev.azure.com/scikit-build/scikit-build/_build/latest?definitionId=1&branchName=master

.. image:: https://codecov.io/gh/scikit-build/scikit-build/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/scikit-build/scikit-build
    :alt: Code coverage status

.. image:: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github
    :target: https://github.com/orgs/scikit-build/discussions
    :alt: GitHub Discussion

Improved build system generator for CPython C/C++/Fortran/Cython extensions.

Better support is available for additional compilers, build systems, cross
compilation, and locating dependencies and determining their build
requirements.

The **scikit-build** package is fundamentally just glue between
the ``setuptools`` Python module and `CMake <https://cmake.org/>`_.

To get started, see `this example <https://scikit-build.readthedocs.io/en/latest/usage.html#example-of-setup-py-cmakelists-txt-and-pyproject-toml>`_ and `scikit-build-sample-projects <https://github.com/scikit-build/scikit-build-sample-projects>`_.


Latest Release
--------------

.. table::

  +-----------------------------------------------------------------------------+-------------------------------------------------------------------------------+
  | Versions                                                                    | Downloads                                                                     |
  +=============================================================================+===============================================================================+
  | .. image:: https://img.shields.io/pypi/v/scikit-build.svg                   | .. image:: https://img.shields.io/pypi/dm/scikit-build                        |
  |     :target: https://pypi.python.org/pypi/scikit-build                      |     :target: https://pypi.python.org/pypi/scikit-build                        |
  +-----------------------------------------------------------------------------+-------------------------------------------------------------------------------+
  | .. image:: https://anaconda.org/conda-forge/scikit-build/badges/version.svg | .. image:: https://anaconda.org/conda-forge/scikit-build/badges/downloads.svg |
  |     :target: https://anaconda.org/conda-forge/scikit-build                  |     :target: https://anaconda.org/conda-forge/scikit-build                    |
  +-----------------------------------------------------------------------------+-------------------------------------------------------------------------------+



Known Issues
------------

These issues are likely to be addressed in upcoming releases.

* Editable installs do not work with the latest versions of Setuptools (and had
  issues with older versions, too).
* Configuration scikit-build cares about _must_ be specified in ``setup()``
  currently.
* The cache directory (``_skbuild``) may need to be deleted between builds in
  some cases (like rebuilding with a different Python interpreter).

We are also working on improving scikit-build, so there are some upcoming
changes and deprecations:


* All deprecated setuptools/distutils features are also deprecated in
  scikit-build, like the ``test`` command, ``easy_install``, etc.
* Python 3.6
  support is deprecated, as setuptools, pytest, and everything else we use has
  dropped it already.
* Older versions of CMake (<3.15) are not recommended; a future version will
  remove support for older CMake's (along with providing a better mechanism for
  ensuring a proper CMake is available).
* Our primary branch will change to ``main``

If you need any of these features, please open or find an issue explaining what
and why you need something.

Miscellaneous
-------------

* Free software: MIT license
* Documentation: http://scikit-build.readthedocs.org
* Source code: https://github.com/scikit-build/scikit-build
* Discussions: https://github.com/orgs/scikit-build/discussions


Support for this work was provided by NSF cooperative agreement `OAC-2209877 <https://www.nsf.gov/awardsearch/showAward?AWD_ID=2209877>`_.
