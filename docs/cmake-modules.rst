=============
CMake modules
=============

To facilitate the writing of ``CMakeLists.txt`` used to build
CPython C/C++/Cython extensions, **scikit-build** provides the following
CMake modules:

.. toctree::
   :maxdepth: 1

   cmake-modules/Cython
   cmake-modules/NumPy
   cmake-modules/PythonExtensions


They can be included using ``find_package``:

.. code-block:: cmake

    find_package(Cython REQUIRED)
    find_package(NumPy REQUIRED)
    find_package(PythonExtensions REQUIRED)


For more details, see the respective documentation of each modules.
