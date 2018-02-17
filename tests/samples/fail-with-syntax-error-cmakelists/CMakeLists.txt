cmake_minimum_required(VERSION 3.5.0)

project(fail_with_syntax_error_cmakelists NONE)

install(CODE "execute_process(COMMAND \${CMAKE_COMMAND} -E sleep 0)")

message(STATUS "This is incorrect  # Parenthesis omitted on purpose
