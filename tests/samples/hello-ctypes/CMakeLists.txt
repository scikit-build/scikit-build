cmake_minimum_required(VERSION 3.5.0)

project(hello LANGUAGES C CXX)

set(SOURCE_FILES
    src/hello.cxx)

add_library(hello SHARED ${SOURCE_FILES})

install(TARGETS hello LIBRARY DESTINATION "hello")

# set compiler-specific flags
if(${CMAKE_CXX_COMPILER_ID} STREQUAL "MSVC")
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
    # Set the DLLEXPORT variable to export symbols
    target_compile_definitions(hello PRIVATE HELLO_WIN_EXPORT)
endif()
