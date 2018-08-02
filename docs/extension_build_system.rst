======================
Extension Build System
======================


Introduction
------------

By default, scikit-build looks in the project top-level directory for a
file named ``CMakeLists.txt``. It will then invoke ``cmake`` executable
specifying a :doc:`generator </generators>` matching the python being used.


How to test if scikit-build is driving the compilation ?
--------------------------------------------------------

To support the case of code base being built as both a standalone project
and a python wheel, it is possible to test for the variable ``SKBUILD``:

.. code-block:: cmake

    if(SKBUILD)
      message(STATUS "The project is built using scikit-build")
    endif()


.. _support_isolated_build:

Support for isolated build
--------------------------

As specified in `PEP 518`_, dependencies required at install time can be specified using a
``pyproject.toml`` file. Starting with pip 10.0, pip reads the ``pyproject.toml`` file and
installs the associated dependencies in an isolated environment. See the `pip build system interface`_
documentation.

An isolated environment will be created when using pip to install packages directly from
source or to create an editable installation.

scikit-build supports these use cases as well as the case where the isolated environment support
is explicitly disabled using the pip option ``--no-build-isolation`` available with the `install`,
`download` and `wheel` commands.

.. _`PEP 518`: https://www.python.org/dev/peps/pep-0518/
.. _'pip build system interface': https://pip.pypa.io/en/stable/reference/pip/#build-system-interface


.. _optimized_incremental_build:

Optimized incremental build
---------------------------

To optimize the developer workflow, scikit-build reconfigures the CMake project only when
needed. It caches the environment associated with the generator as well as the CMake execution
properties.

The CMake properties are saved in a :const:`CMake spec file <skbuild.constants.CMAKE_SPEC_FILE>` responsible
to store the CMake executable path, the CMake configuration arguments, the CMake version as well as the
environment variables ``PYTHONNOUSERSITE`` and ``PYTHONPATH``.

If there are no ``CMakeCache.txt`` file or if any of the CMake properties changes, scikit-build will
explicitly reconfigure the project calling :meth:`skbuild.cmaker.CMaker.configure`.

If a file is added to the CMake build system by updating one of the ``CMakeLists.txt`` file, scikit-build
will not explicitly reconfigure the project. Instead, the generated build-system will automatically
detect the change and reconfigure the project after :meth:`skbuild.cmaker.CMaker.make` is called.
