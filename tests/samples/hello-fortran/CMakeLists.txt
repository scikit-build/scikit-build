cmake_minimum_required(VERSION 3.5.0)

project(hello_fortran C Fortran)

find_package(PythonExtensions REQUIRED)
find_package(NumPy REQUIRED)

add_subdirectory(hello)
