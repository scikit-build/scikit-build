==============================================
C Runtime, Compiler and Build System Generator
==============================================

scikit-build uses sensible defaults allowing to select the C runtime matching
the `official CPython <https://www.python.org/>`_ recommendations. It also
ensures developers remain productive by selecting an alternative environment if
recommended one is not available.

The table below lists the different C runtime implementations, compilers and
their usual distribution mechanisms for each operating systems.

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


Build system generator
----------------------

Since scikit-build simply provides glue between ``setuptools``
and ``CMake``, it needs to choose a `CMake generator`_ to configure the build
system allowing to build of CPython C extensions.

.. _CMake generator: https://cmake.org/cmake/help/latest/manual/cmake-generators.7.html

The table below lists the generator supported by scikit-build:

.. table::

    +----------------------+---------+------------+--------------------------------------------------+
    | **Operating System** | Linux   | MacOSX     | Windows                                          |
    +======================+=========+============+==================================================+
    | **CMake Generator**  | 1. `Ninja`_          | 1. `Ninja`_                                      |
    |                      | 2. `Unix Makefiles`_ | 2. `Visual Studio`_                              |
    |                      |                      | 3. `NMake Makefiles`_                            |
    |                      |                      | 4. :ref:`NMake Makefiles JOM <NMake Makefiles>`  |
    +----------------------+----------------------+--------------------------------------------------+

When building a project, scikit-build iteratively tries each generator (in
the order listed in the table) until it finds a working one.

For more details about CMake generators, see `CMake documentation <https://cmake.org/cmake/help/latest/manual/cmake-generators.7.html>`_.

.. _Ninja:

Ninja
^^^^^

- Supported platform(s): Linux, MacOSX and Windows

- If `ninja executable <https://ninja-build.org>`_ is in the ``PATH``, the associated
  generator is used to setup the project build system based on ``ninja`` files.

- In a given python environment, installing the `ninja python package <https://pypi.org/project/ninja/>`_
  with ``pip install ninja`` will ensure that ninja is in the ``PATH``.

.. note:: **Automatic parallelism**

    An advantage of ninja is that it automatically parallelizes the build based on the
    number of CPUs. See :ref:`usage_enabling_parallel_build`.

.. note:: **Ninja on Windows**

    When `Ninja` generator is used on Windows, scikit-build will make sure the
    project is configured and built with the appropriate [#automaticvsenv]_
    environment (equivalent of calling ``vcvarsall.bat x86``
    or ``vcvarsall.bat amd64``).


    When Visual Studio >= 2017 is used, ninja is available by default thanks to
    the Microsoft CMake extension:

    ::

        C:/Program Files (x86)/Microsoft Visual Studio/2017/Professional/Common7/IDE/CommonExtensions/Microsoft/CMake/Ninja/ninja.exe


.. _Unix Makefiles:

Unix Makefiles
^^^^^^^^^^^^^^

- Supported platform(s): Linux, MacOSX

- scikit-build uses this generator to generate a traditional ``Makefile`` based
  build system.


.. _Visual Studio IDE:

Visual Studio IDE
^^^^^^^^^^^^^^^^^

- Supported platform(s): Windows

- scikit-build uses the generator corresponding to selected version of
  Visual Studio and generate a ``solution file`` based build system.

.. table::

    +-------------------+------------------------------------------------------+
    |                   | Architecture                                         |
    +-------------------+------------------------+-----------------------------+
    | CPython Version   | x86 (32-bit)           | x64 (64-bit)                |
    +===================+========================+=============================+
    | **3.7 and above** | Visual Studio 17 2022  | Visual Studio 17 2022 Win64 |
    |                   | Visual Studio 16 2019  | Visual Studio 16 2019 Win64 |
    |                   | Visual Studio 15 2017  | Visual Studio 15 2017 Win64 |
    +-------------------+------------------------+-----------------------------+


.. note::

    The Visual Studio generators can not be used when only :ref:`alternative environments <table-vs_download_links>`
    are installed, in that case :ref:`Ninja` or :ref:`NMake Makefiles` are used.


.. _NMake Makefiles:

NMake Makefiles
^^^^^^^^^^^^^^^

- Supported platform(s): Windows

- scikit-build will make sure the project is configured and built with the
  appropriate [#automaticvsenv]_ environment (equivalent of calling
  ``vcvarsall.bat x86`` or ``vcvarsall.bat amd64``).

.. note:: **NMake Makefiles JOM**

    The `NMake Makefiles JOM` generator is supported **but** it is not automatically
    used by scikit-build (even if `jom executable <https://wiki.qt.io/Jom>`_ is in the ``PATH``),
    it always needs to be explicitly specified. For example::

      python setup.py build -G "NMake Makefiles JOM"

    For more details, see :ref:`usage_scikit-build_options`.

Linux
-----

scikit-build uses the toolchain set using ``CC`` (and ``CXX``) environment variables. If
no environment variable is set, it defaults to ``gcc``.

To build compliant Linux wheels, scikit-build also supports the ``manylinux``
platform described in `PEP-0513 <https://www.python.org/dev/peps/pep-0513/>`_. We
recommend the use of `dockcross/manylinux-x64 <https://github.com/dockcross/dockcross>`_ and
`dockcross/manylinux-x86 <https://github.com/dockcross/dockcross>`_. These images are
optimized for building Linux wheels using scikit-build.

MacOSX
------

scikit-build uses the toolchain set using ``CC`` (and ``CXX``) environment variables. If
no environment variable is set, it defaults to the `Apple compiler`_ installed with XCode.

.. _Apple compiler: https://en.wikipedia.org/wiki/Xcode#Toolchain_versions

Default Deployment Target and Architecture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. versionadded:: 0.7.0

The default deployment target and architecture selected by scikit-build are
hard-coded for MacOSX and are respectively ``10.9`` and ``x86_64``.

This means that the platform name associated with the ``bdist_wheel``
command is::

    macosx-10.9-x86_64

and is equivalent to building the wheel using::

    python setup.py bdist_wheel --plat-name macosx-10.9-x86_64

Respectively, the values associated with the corresponding `CMAKE_OSX_DEPLOYMENT_TARGET`_
and `CMAKE_OSX_ARCHITECTURES`_ CMake options that are automatically used to configure
the project are the following::

    CMAKE_OSX_DEPLOYMENT_TARGET:STRING=10.9
    CMAKE_OSX_ARCHITECTURES:STRING=x86_64

.. _CMAKE_OSX_DEPLOYMENT_TARGET: https://cmake.org/cmake/help/latest/variable/CMAKE_OSX_DEPLOYMENT_TARGET.html
.. _CMAKE_OSX_ARCHITECTURES: https://cmake.org/cmake/help/latest/variable/CMAKE_OSX_ARCHITECTURES.html

As illustrated in the table below, choosing ``10.9`` as deployment target to build
MacOSX wheels will allow them to work on ``System CPython``, the ``Official CPython``,
``Macports`` and also ``Homebrew`` installations of CPython.

.. table:: List of platform names for each CPython distributions, CPython and OSX versions.

    +----------------------+-------------------------+--------------+--------------------------------+
    | CPython Distribution | CPython Version         | OSX Version  | ``get_platform()`` [#getplat]_ |
    +======================+=========================+==============+================================+
    | Official CPython     | 3.9, 3.10               | 10.9         | macosx-10.9-universal2         |
    |                      +-------------------------+--------------+--------------------------------+
    |                      | 3.8                     | 11           | macosx-11.0-universal2         |
    |                      +-------------------------+--------------+--------------------------------+
    |                      | 3.7, 3.8, 3.9, 3.10     | 10.9         | macosx-10.9-x86_64             |
    +----------------------+-------------------------+--------------+--------------------------------+
    | Macports CPython     | 3.x                     | Current      | Depends on current macOS       |
    +----------------------+-------------------------+--------------+ version.                       |
    | Homebrew CPython     | 3.x                     | Current      |                                |
    +----------------------+-------------------------+--------------+--------------------------------+


The information above have been adapted from the excellent `Spinning wheels`_
article written by Matthew Brett.

.. _Spinning wheels: https://github.com/MacPython/wiki/wiki/Spinning-wheels


Default SDK and customization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. versionadded:: 0.7.0

By default, scikit-build lets CMake discover the most recent SDK available on the
system during the configuration of the project. CMake internally uses the logic
implemented in the `Platform/Darwin-Initialize.cmake`_ CMake module.

.. _Platform/Darwin-Initialize.cmake: https://github.com/Kitware/CMake/blob/master/Modules/Platform/Darwin-Initialize.cmake


Customizing SDK
^^^^^^^^^^^^^^^

.. versionadded:: 0.7.0

If needed, this can be overridden by explicitly passing the CMake option
`CMAKE_OSX_SYSROOT`_. For example::

    python setup.py bdist_wheel -- -DCMAKE_OSX_SYSROOT:PATH=/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.12.sdk

.. _CMAKE_OSX_SYSROOT: https://cmake.org/cmake/help/latest/variable/CMAKE_OSX_SYSROOT.html

Customizing Deployment Target and Architecture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. versionadded:: 0.11.0

Deployment target can be customized by setting the ``MACOSX_DEPLOYMENT_TARGET``
environment variable.

.. versionadded:: 0.7.0

Deployment target and architecture can be customized by associating the
``--plat-name macosx-<deployment_target>-<arch>`` option with the ``bdist_wheel``
command.

For example::

    python setup.py bdist_wheel --plat-name macosx-10.9-x86_64


scikit-build also sets the value of `CMAKE_OSX_DEPLOYMENT_TARGET`_ and
`CMAKE_OSX_ARCHITECTURES`_ option based on the provided platform name. Based on
the example above, the options used to configure the associated CMake project
are::

    -DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=10.9
    -DCMAKE_OSX_ARCHITECTURES:STRING=x86_64

libstdc++ vs libc++
^^^^^^^^^^^^^^^^^^^

Before OSX 10.9, the default was ``libstdc++``.

With OSX 10.9 and above, the default is ``libc++``.

Forcing the use of ``libstdc++`` on newer version of OSX is still possible using the
flag ``-stdlib=libstdc++``. That said, doing so will report the following warning::

    clang: warning: libstdc++ is deprecated; move to libc++


* `libstdc++ <https://gcc.gnu.org/onlinedocs/libstdc++/>`_:

    This is the GNU Standard C++ Library v3 aiming to implement the ISO 14882 Standard C++ library.

* `libc++ <https://libcxx.llvm.org/docs/>`_:

    This is a new implementation of the C++ standard library, targeting C++11.


Windows
-------

Microsoft C run-time and Visual Studio version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On windows, scikit-build looks for the version of Visual Studio matching the
version of CPython being used. The selected Visual Studio version also defines
which Microsoft C run-time and compiler are used:

.. table::

    +---------------------------+-----------------+
    | Python version            | 3.7 and above   |
    +===========================+=================+
    | **Microsoft C run-time**  | `ucrtbase.dll`_ |
    +---------------------------+-----------------+
    | **Compiler version**      | MSVC++ 14.0     |
    +---------------------------+-----------------+
    | **Visual Studio version** | 2017            |
    +---------------------------+-----------------+

.. _ucrtbase.dll: https://msdn.microsoft.com/en-us/library/abx4dbyh(v=vs.140).aspx

Installing compiler and Microsoft C run-time
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As outlined above, installing a given version of Visual Studio will
automatically install the corresponding compiler along with the
Microsoft C run-time libraries.

This means that if you already have the corresponding version of Visual Studio
installed, your environment is ready.

Nevertheless, since older version of Visual Studio are not available anymore,
this next table references links for installing alternative environments:

.. _table-vs_download_links:

.. table:: Download links for Windows SDK and Visual Studio.

    +-------------------+-------------------------------------------------+
    | CPython version   | Download links for Windows SDK or Visual Studio |
    +===================+=================================================+
    | **3.7 and above** | - `Visual C++ Build Tools`_                     |
    |                   |                                                 |
    |                   | or                                              |
    |                   |                                                 |
    |                   | - `Visual Studio`_  (2017 or newer)             |
    +-------------------+-------------------------------------------------+

These links have been copied from the great article [#alternativevs]_ of
Steve Dower, engineer at Microsoft.

.. _Visual C++ Build Tools: https://visualstudio.microsoft.com/downloads/
.. _Visual Studio: https://visualstudio.microsoft.com/downloads/
.. _Windows SDK for Windows 7 and .NET 4.0: https://www.microsoft.com/download/details.aspx?id=8279


.. rubric:: Footnotes

.. [#getplat] ``from distutils.util import get_platform; print(get_platform())``

.. [#alternativevs] `How to deal with the pain of "unable to find vcvarsall.bat" <https://blogs.msdn.microsoft.com/pythonengineering/2016/04/11/unable-to-find-vcvarsall-bat/>`_

.. [#automaticvsenv] Implementation details: This is made possible by internally using the function ``query_vcvarsall``
                     from ``distutils._msvccompiler``. To ensure, the environment associated with the latest compiler is properly detected, the
                     ``distutils`` modules are systematically patched using ``setuptools.monkey.patch_for_msvc_specialized_compiler()``.
