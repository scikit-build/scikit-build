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

The main runtime dependency is ``scikit-build-core[setuptools]``, which
provides the build backend. The full list of dependencies can be seen in
``pyproject.toml``.

Compiler Toolchain
^^^^^^^^^^^^^^^^^^

The same compiler toolchain used to build the CPython interpreter should also
be available. Refer to the
`CPython Developer's Guide <https://devguide.python.org/getting-started/setup-building/#install-dependencies>`_
for details about the compiler toolchain for your operating system.

For example, on *Ubuntu Linux*, install with::

    $ sudo apt-get install build-essential

On *macOS*, install `Xcode <https://developer.apple.com/xcode/>`_ or the
command line tools (``xcode-select --install``).

On *Windows*, install `Visual Studio
<https://visualstudio.microsoft.com/visual-cpp-build-tools/>`_ with the C++
workload.

.. _installation_cmake:

CMake
^^^^^

The easiest way to get `CMake <https://www.cmake.org/>`_ is :ref:`to add it to
the pyproject.toml file <basic_usage_example>`. The CMake Python package is
then downloaded and installed when your project is built.

To manually install the *cmake* package from PyPI::

    $ pip install cmake

To install the *cmake* package in conda::

    $ conda install -c conda-forge cmake

You can also `download the standard CMake binaries
<https://cmake.org/download>`_ for your platform.

Alternatively, `build CMake from source <https://cmake.org/install/>`_ with a
C++ compiler if binaries are not available for your operating system.
