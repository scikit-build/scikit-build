==============================================
C Runtime, Compiler and Build System Generator
==============================================

Build system generator
----------------------

Since scikit-build simply provides glue between ``setuptools``
and ``CMake``, a `CMake generator`_ is used to configure the build
system allowing to build of CPython C extensions.

.. _CMake generator: https://cmake.org/cmake/help/latest/manual/cmake-generators.7.html

.. versionchanged:: 1.0

    scikit-build no longer probes for installed Visual Studio versions or
    runs a language test to discover a working generator. CMake's own
    default generator selection applies.

CMake selects its default generator for the current platform, and the
``CMAKE_GENERATOR`` environment variable can be used to override it::

    CMAKE_GENERATOR="Unix Makefiles" pip install .

``Ninja`` is the recommended generator. It is automatically parallel and is
available on all platforms; listing the `ninja python package
<https://pypi.org/project/ninja/>`_ in the ``build-system.requires`` table of
your ``pyproject.toml`` (see :ref:`basic_usage_example`) ensures it is
available during the build. On Windows, MSVC 2017 and newer ship with Ninja
already, so ``ninja`` can be limited to non-Windows systems in
``build-system.requires``.

For more details about CMake generators, see the `CMake documentation
<https://cmake.org/cmake/help/latest/manual/cmake-generators.7.html>`_.

Compiler
--------

The compiler is selected by CMake following its usual rules; the ``CC`` and
``CXX`` environment variables can be used to point at specific compilers.
The compiler toolchain used to build the target CPython interpreter should
be available; refer to the table below for the usual distribution mechanisms
for each operating system.

.. table::

    +------------------+---------------------------+-------------------------+-----------------------------------+
    |                  | Linux                     | MacOSX                  | Windows                           |
    +==================+===========================+=========================+===================================+
    | **C runtime**    | `GNU C Library (glibc)`_  | `libSystem library`_    | `Microsoft C run-time library`_   |
    +------------------+---------------------------+-------------------------+-----------------------------------+
    | **Compiler**     | `GNU compiler (gcc)`_     | `clang`_                | Microsoft C/C++ Compiler (cl.exe) |
    +------------------+---------------------------+-------------------------+-----------------------------------+
    | **Provenance**   | `Package manager`_        | OSX SDK within `XCode`_ | - `Microsoft Visual Studio`_      |
    |                  |                           |                         | - `Microsoft Windows SDK`_        |
    +------------------+---------------------------+-------------------------+-----------------------------------+

.. _GNU C Library (glibc): https://en.wikipedia.org/wiki/GNU_C_Library
.. _Package manager: https://en.wikipedia.org/wiki/Package_manager
.. _Microsoft C run-time library: https://en.wikipedia.org/wiki/Microsoft_Windows_library_files#Runtime_libraries
.. _libSystem library: https://www.safaribooksonline.com/library/view/mac-os-x/0596003560/ch05s02.html
.. _XCode: https://en.wikipedia.org/wiki/Xcode#Version_comparison_table
.. _Microsoft Windows SDK: https://en.wikipedia.org/wiki/Microsoft_Windows_SDK
.. _Microsoft Visual Studio: https://en.wikipedia.org/wiki/Microsoft_Visual_Studio
.. _GNU compiler (gcc): https://en.wikipedia.org/wiki/GNU_Compiler_Collection
.. _clang: https://en.wikipedia.org/wiki/Clang
