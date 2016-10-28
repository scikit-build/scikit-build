======================
Extension Build System
======================


Introduction
------------

By default, scikit-build looks in the project top-level directory for a
file named ``CMakeLists.txt``. It will then invoke ``cmake`` executable
specifying a generator matching the python being used.

Indeed, each CPython version is associated with an official compiler. By
default, scikit-build will automatically select the compiler, associated
C runtime, and build flags matching the official recommendations:


How to test if scikit-build is driving the compilation ?
--------------------------------------------------------

To support the case of code base being built as both a standalone project
and a python wheel, it is possible to test for the variable ``SKBUILD``:

.. code-block:: cmake

    if(SKBUILD)
      message(STATUS "The project is built using scikit-build")
    endif()
