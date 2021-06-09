cmake_minimum_required(VERSION 3.5.0)

project(hello NONE)

install(CODE "execute_process(COMMAND \${CMAKE_COMMAND} -E sleep 0)")
