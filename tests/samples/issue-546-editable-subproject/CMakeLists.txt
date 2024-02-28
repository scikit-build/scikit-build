cmake_minimum_required(VERSION 3.15)

project(testpkg VERSION 0.1 LANGUAGES CXX)

set(PYBIND11_FINDPYTHON TRUE)

find_package(pybind11 CONFIG PATHS ${pybind11_SEARCH_PATH} REQUIRED)

pybind11_add_module(_pkg src/pkg/module.cpp)

set_target_properties(_pkg PROPERTIES CXX_STANDARD 11)
target_include_directories(_pkg PRIVATE ${pybind11_INCLUDE_DIRS})

install(TARGETS _pkg LIBRARY DESTINATION .)
