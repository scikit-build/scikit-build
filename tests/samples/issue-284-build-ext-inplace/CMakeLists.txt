cmake_minimum_required(VERSION 3.5.0)

project(hello)

find_package(PythonExtensions REQUIRED)

add_library(_hello_sk MODULE hello/_hello_sk.cxx)
python_extension_module(_hello_sk)

install(TARGETS _hello_sk LIBRARY DESTINATION hello)
