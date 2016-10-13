cmake_minimum_required(VERSION 3.5.0)

project(hello)

find_package(PythonInterp REQUIRED)
find_package(PythonLibs REQUIRED)
find_package(PythonExtensions REQUIRED)

add_subdirectory(hello)
