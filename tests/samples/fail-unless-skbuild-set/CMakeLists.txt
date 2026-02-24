cmake_minimum_required(VERSION 3.5...3.26)

project(fail_unless_skbuild_set NONE)

if(NOT DEFINED SKBUILD)
  message(FATAL_ERROR "SKBUILD is not set!")
endif()

install(CODE "execute_process(COMMAND \${CMAKE_COMMAND} -E sleep 0)")
