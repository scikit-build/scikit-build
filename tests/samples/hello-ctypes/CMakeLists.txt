cmake_minimum_required(VERSION 3.13.0)

project(hello LANGUAGES C CXX)

set(SOURCE_FILES
    src/hello.cxx)

#add_library(hello SHARED ${SOURCE_FILES})
add_library(hello MODULE ${SOURCE_FILES})

# set compiler-specific flags
if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "MSVC")
    # Set the DLLEXPORT variable to export symbols
    target_compile_definitions(hello PRIVATE HELLO_WIN_EXPORT)
endif()

install(TARGETS hello LIBRARY DESTINATION "hello")
