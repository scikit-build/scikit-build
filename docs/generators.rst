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

Since scikit-build simply provides glue between `setuptools`
and `CMake`, it needs to choose a `CMake generator`_ to configure the build
system allowing to build of CPython C extensions.

.. _CMake generator: https://cmake.org/cmake/help/v3.7/manual/cmake-generators.7.html

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

For more details about CMake generators, see `CMake documentation <https://cmake.org/cmake/help/v3.7/manual/cmake-generators.7.html>`_.

.. _Ninja:

Ninja
^^^^^

- Supported platform(s): Linux, MacOSX and Windows

- If `ninja executable <https://ninja-build.org>`_ is in the ``PATH``, the associated
  generator is used to setup the project build system based on ``ninja`` files.

.. note:: **Automatic parallelism**

    An advantage of ninja is that it automatically parallelizes the build based on the
    number of CPUs.

.. note:: **Ninja on Windows**

    When `Ninja` generator is used on Windows, scikit-build will make sure the
    project is configured and built with the appropriate [#automaticvsenv]_
    environment (equivalent of calling ``vcvarsall.bat x86``
    or ``vcvarsall.bat amd64``).


.. _Unix Makefiles:

Unix Makefiles
^^^^^^^^^^^^^^

- Supported platform(s): Linux, MacOSX

- scikit-build uses this generator to generate a traditional ``Makefile`` based
  build system.


.. _Visual Studio:

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
    | **3.5 and above** | Visual Studio 14 2015  | Visual Studio 14 2008 Win64 |
    +-------------------+------------------------+-----------------------------+
    | **3.3 to 3.4**    | Visual Studio 10 2010  | Visual Studio 10 2010 Win64 |
    +-------------------+------------------------+-----------------------------+
    | **2.7 to 3.2**    | Visual Studio 9 2008   | Visual Studio 9 2008 Win64  |
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

.. note:: *To be documented*

    See https://github.com/MacPython/wiki/wiki/Spinning-wheels


Windows
-------

Microsoft C run-time and Visual Studio version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On windows, scikit-build looks for the version of Visual Studio matching the
version of CPython being used. The selected Visual Studio version also defines
which Microsoft C run-time and compiler are used:

.. table::

    +---------------------------+----------------+-----------------+-----------------+
    | Python version            | 2.7 to 3.2     | 3.3 to 3.4      | 3.5 and above   |
    +===========================+================+=================+=================+
    | **Microsoft C run-time**  | `msvcr90.dll`_ | `msvcr100.dll`_ | `ucrtbase.dll`_ |
    +---------------------------+----------------+-----------------+-----------------+
    | **Compiler version**      | MSVC++ 9.0     | MSVC++ 10.0     | MSVC++ 14.0     |
    +---------------------------+----------------+-----------------+-----------------+
    | **Visual Studio version** | 2008           | 2010            | 2015            |
    +---------------------------+----------------+-----------------+-----------------+

.. _msvcr90.dll: https://msdn.microsoft.com/en-us/library/abx4dbyh(v=vs.90).aspx
.. _msvcr100.dll: https://msdn.microsoft.com/en-us/library/abx4dbyh(v=vs.100).aspx
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
    | **3.5 and above** | - `Visual C++ Build Tools 2015`_                |
    |                   |                                                 |
    |                   | or                                              |
    |                   |                                                 |
    |                   | - `Visual Studio 2015`_                         |
    +-------------------+-------------------------------------------------+
    | **3.3 to 3.4**    | `Windows SDK for Windows 7 and .NET 4.0`_       |
    +-------------------+-------------------------------------------------+
    | **2.7 to 3.2**    | `Microsoft Visual C++ Compiler for Python 2.7`_ |
    +-------------------+-------------------------------------------------+

These links have been copied from the great article [#alternativevs]_ of
Steve Dower, engineer at Microsoft.

.. _Visual C++ Build Tools 2015: http://go.microsoft.com/fwlink/?LinkId=691126
.. _Visual Studio 2015: https://visualstudio.com/
.. _Windows SDK for Windows 7 and .NET 4.0: https://www.microsoft.com/download/details.aspx?id=8279
.. _Microsoft Visual C++ Compiler for Python 2.7: http://aka.ms/vcpython27


.. rubric:: Footnotes

.. [#alternativevs] `How to deal with the pain of “unable to find vcvarsall.bat” <https://blogs.msdn.microsoft.com/pythonengineering/2016/04/11/unable-to-find-vcvarsall-bat/>`_

.. [#automaticvsenv] Implementation details: This is made possible by internally using the function ``query_vcvarsall``
                     from the ``distutils.msvc9compiler`` (or ``distutils._msvccompiler`` when visual studio ``>= 2015``
                     is used). To ensure, the environment associated with the latest compiler is properly detected, the
                     ``distutils`` modules are systematically patched using ``setuptools.monkey.patch_for_msvc_specialized_compiler()``.
