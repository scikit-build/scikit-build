cmake_minimum_required(VERSION 3.5.0)

project(fail_with_fatal_error_cmakelists NONE)

install(CODE "execute_process(COMMAND \${CMAKE_COMMAND} -E sleep 0)")

message(FATAL_ERROR "Invalid CMakeLists.txt")
