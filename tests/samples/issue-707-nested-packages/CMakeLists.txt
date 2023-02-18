cmake_minimum_required(VERSION 3.5...3.22)

project(hello_cython)

find_package(PythonExtensions REQUIRED)
find_package(Cython REQUIRED)

add_cython_target(_hello hello/_hello.pyx CXX)
add_library(_hello MODULE ${_hello})
python_extension_module(_hello)

install(TARGETS _hello LIBRARY DESTINATION hello)

add_cython_target(_goodbye hello/goodbye/_goodbye.pyx CXX)
add_library(_goodbye MODULE ${_goodbye})
python_extension_module(_goodbye)

install(TARGETS _goodbye LIBRARY DESTINATION hello/goodbye)
