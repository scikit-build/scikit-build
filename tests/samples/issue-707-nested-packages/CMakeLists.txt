cmake_minimum_required(VERSION 3.5...3.22)

project(hello_nested)

find_package(PythonExtensions REQUIRED)
find_package(Cython REQUIRED)

add_cython_target(_hello_nested hello_nested/_hello_nested.pyx CXX)
add_library(_hello_nested MODULE ${_hello_nested})
python_extension_module(_hello_nested)

install(TARGETS _hello_nested LIBRARY DESTINATION hello_nested)

add_cython_target(_goodbye_nested hello_nested/goodbye_nested/_goodbye_nested.pyx CXX)
add_library(_goodbye_nested MODULE ${_goodbye_nested})
python_extension_module(_goodbye_nested)

install(TARGETS _goodbye_nested LIBRARY DESTINATION hello_nested/goodbye_nested)
