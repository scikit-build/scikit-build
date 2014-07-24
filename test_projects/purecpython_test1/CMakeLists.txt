cmake_minimum_required (VERSION 2.8.1 FATAL_ERROR)

project(PyCMakePureCPythonTest)

#
# Use standard CMake package to find Python. This should be passed
# from PyCMake.
#
find_package(PythonInterp ${PYTHON_VERSION_STRING} EXACT ${_QUIET} REQUIRED)
find_package(PythonLibs ${PYTHON_VERSION_STRING} EXACT ${_QUIET} REQUIRED)

ADD_SUBDIRECTORY(test1)
