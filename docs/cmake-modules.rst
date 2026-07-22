=============
CMake modules
=============

To facilitate the writing of ``CMakeLists.txt`` used to build
CPython C/C++/Cython extensions, **scikit-build** provides the following
historical CMake modules:

.. toctree::
   :maxdepth: 1

   cmake-modules/Cython
   cmake-modules/NumPy
   cmake-modules/PythonExtensions
   cmake-modules/F2PY


They can be included using ``find_package``:

.. code-block:: cmake

    find_package(Cython REQUIRED)
    find_package(NumPy REQUIRED)
    find_package(PythonExtensions REQUIRED)
    find_package(F2PY REQUIRED)


For more details, see the respective documentation of each modules.

New code should not use these. The recommended replacements:

* ``Cython`` -> cython-cmake (on PyPI)
* ``NumPy`` -> FindPython with NumPy component (CMake built-in)
* ``PythonExtensions`` -> FindPython (CMake built-in)
* ``F2PY`` -> f2py-cmake (on PyPI)
