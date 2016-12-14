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
