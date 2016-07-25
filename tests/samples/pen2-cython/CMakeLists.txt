cmake_minimum_required(VERSION 3.5.0)

project(pen2_cython)

enable_testing()

find_package(PythonInterp REQUIRED)
find_package(PythonLibs REQUIRED)
find_package(PythonExtensions REQUIRED)
find_package(Cython REQUIRED)

add_subdirectory(src)
add_subdirectory(scripts)

