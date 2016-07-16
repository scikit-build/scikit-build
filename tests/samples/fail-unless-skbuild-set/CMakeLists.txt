cmake_minimum_required(VERSION 3.5.0)

project(fail_unless_skbuild_set)

if(NOT DEFINED SKBUILD)
  message(FATAL_ERROR "SKBUILD is not set!")
endif()

