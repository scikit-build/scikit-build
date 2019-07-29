cmake_minimum_required(VERSION 3.5.0)

project(hello LANGUAGES C CXX)

set(SOURCE_FILES
    src/hello.cxx)

add_library(hello SHARED ${SOURCE_FILES})

install(TARGETS hello LIBRARY DESTINATION "hello")
