cmake_minimum_required(VERSION 3.5.0)

project(hello_cython)

include(CTest)
enable_testing()

set(CMAKE_MODULE_PATH
    ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/../cmake-files)

find_package(PythonInterp REQUIRED)
find_package(PythonLibs REQUIRED)
find_package(PythonExtensions REQUIRED)
find_package(Cython REQUIRED)

add_subdirectory(hello)
