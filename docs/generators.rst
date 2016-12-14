==================
Compiler Selection
==================

Each CPython version is associated with an official compiler. By
default, scikit-build will automatically select the compiler, associated
C runtime, and build flags matching the official recommendations:

Windows
-------

scikit-build will look for the version of Visual Studio matching the version
of python being used:

================================================================ =================== ==================
2.7 to 3.2                                                       3.3 to 3.4          3.5 and above
================================================================ =================== ==================
Visual Studio 2008                                               Visual Studio 2010  Visual Studio 2015
`Visual C++ Compiler for Python 2.7 <http://aka.ms/vcpython27>`_
================================================================ =================== ==================

If `ninja executable <https://ninja-build.org>`_ is in the ``PATH``, the
corresponding `Ninja <https://cmake.org/cmake/help/v3.7/generator/Ninja.html>`_
CMake generator is used to setup the project build system based on ``ninja`` files.
Otherwise, scikit-build uses the associated
`Visual Studio IDE <https://cmake.org/cmake/help/v3.7/manual/cmake-generators.7.html#visual-studio-generators>`_ generator
to generate a ``solution file`` based build system.
Finally, if neither `Ninja` or `Visual Studio IDE` generators are available (this is the case
with `Visual C++ Compiler for Python 2.7`), scikit-build will
use `NMake Makefiles <https://cmake.org/cmake/help/v3.7/generator/NMake%20Makefiles.html>`_ generator.

When `Ninja` generator is used, scikit-build will make sure the project is configured and built with
the appropriate environment (equivalent of calling ``vcvarsall.bat x86`` or ``vcvarsall.bat amd64``).

`NMake Makefiles <https://cmake.org/cmake/help/v3.7/generator/NMake%20Makefiles.html>`_
and `NMake Makefiles JOM <https://cmake.org/cmake/help/v3.7/generator/NMake%20Makefiles%20JOM.html>`_ also
work out-of-the-box **without** requiring to manually calling ``vcvarsall.bat`` to set the environment.

Implementation details: This is made possible by internally using the function ``query_vcvarsall``
from the ``distutils.msvc9compiler`` (or ``distutils._msvccompiler`` when visual studio ``>= 2015``
is used). To ensure, the environment associated with the latest compiler is properly detected, the
``distutils`` modules are systematically patched using ``setuptools.monkey.patch_for_msvc_specialized_compiler()``.

Linux
-----

scikit-build will automatically find the toolchain available in the current
environment.

If `ninja executable <https://ninja-build.org>`_ is in the ``PATH``, the
corresponding `Ninja <https://cmake.org/cmake/help/v3.7/generator/Ninja.html>`_
CMake generator is used to setup the project build system based on ``ninja`` files.
Otherwise, scikit-build uses `Unix Makefiles <https://cmake.org/cmake/help/v3.7/generator/Unix%20Makefiles.html>`_
CMake generator to generate a traditional ``Makefile`` based build system.

An advantage of ninja is that it automatically parallelizes the build based on the
number of CPUs.

scikit-build also supports ``manylinux`` platform described in `PEP-0513 <https://www.python.org/dev/peps/pep-0513/>`_.
When building wheels for Linux we recommend the use of `dockcross/manylinux-x64 <https://github.com/dockcross/dockcross>`_ and
`dockcross/manylinux-x86 <https://github.com/dockcross/dockcross>`_. These images are optimized for building Linux wheels.


MacOSX
------

scikit-build will automatically find the toolchain available in the current
environment.

If `ninja executable <https://ninja-build.org>`_ is in the ``PATH``, the
corresponding `Ninja <https://cmake.org/cmake/help/v3.7/generator/Ninja.html>`_
CMake generator is used to setup the project build system based on ``ninja`` files.
Otherwise, scikit-build uses `Unix Makefiles <https://cmake.org/cmake/help/v3.7/generator/Unix%20Makefiles.html>`_
CMake generator to generate a traditional ``Makefile`` based build system.
