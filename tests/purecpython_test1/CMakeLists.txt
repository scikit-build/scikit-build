cmake_minimum_required (VERSION 2.8.1 FATAL_ERROR)

project(PyCMakePureCPythonTest)

#
# Use standard CMake package to find Python. This should be passed
# from PyCMake.
#
find_package(PythonInterp REQUIRED)
find_package(PythonLibs REQUIRED)


add_library(test1 MODULE src/test1.c)

include_directories(${PYTHON_INCLUDE_DIRS})
target_link_libraries(test1 ${PYTHON_LIBRARIES})
