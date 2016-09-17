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

The project has a few common Python package dependencies. The runtime
dependencies are:

.. include:: ../requirements.txt
   :literal:

The build time dependencies (also required for development) are:

.. include:: ../requirements-dev.txt
   :literal:

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

CMake
^^^^^

`Download standard CMake binaries <https://cmake.org/download>`_ for your
platform. Alternatively, build CMake from source with a C++ compiler if
binaries are not available for your operating system.
