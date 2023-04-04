============
Installation
============

Install package with pip
------------------------

To install with pip::

    $ pip install scikit-build

Install from source
-------------------

To install scikit-build from the latest source, first obtain the source code::

    $ git clone https://github.com/scikit-build/scikit-build
    $ cd scikit-build

then install with::

    $ pip install .

or::

    $ pip install -e .

for development.


Dependencies
------------

Python Packages
^^^^^^^^^^^^^^^

The project has a few common Python package dependencies. These can be seen in
``setup.py`` and ``pyproject.toml``.

Compiler Toolchain
^^^^^^^^^^^^^^^^^^

The same compiler toolchain used to build the CPython interpreter should also
be available. Refer to the
`CPython Developer's Guide <https://docs.python.org/devguide/setup.html#build-dependencies>`_
for details about the compiler toolchain for your operating system.

For example, on *Ubuntu Linux*, install with::

    $ sudo apt-get install build-essential

On *Mac OSX*, install `XCode <https://developer.apple.com/xcode/>`_ to build
packages for the system Python.

On Windows, install `the version of Visual Studio used to create the target
version of CPython <https://docs.python.org/devguide/setup.html#windows>`_

.. _installation_cmake:

CMake
^^^^^

The easiest way to get `CMake <https://www.cmake.org/>`_ is :ref:`to add it to
the pyproject.toml file <basic_usage_example>`.  With pip 10 or later, this
will cause the CMake Python package to be downloaded and installed when your
project is built.

To manually install the *cmake* package from PyPI::

    $ pip install cmake

To install the *cmake* package in conda::

    $ conda install -c conda-forge cmake

You can also `download the standard CMake binaries
<https://cmake.org/download>`_ for your platform.

Alternatively, `build CMake from source <https://cmake.org/install/>`_ with a
C++ compiler if binaries are not available for your operating system.
