cmake_minimum_required(VERSION 3.5.0)

project(hello_fortran C Fortran)

find_package(PythonExtensions REQUIRED)
find_package(NumPy REQUIRED)
find_package(F2PY REQUIRED)

add_subdirectory(hello)
add_subdirectory(bonjour)
