cmake_minimum_required(VERSION 3.5.0)

project(hello)

find_package(PythonInterp REQUIRED)
find_package(PythonLibs REQUIRED)
find_package(PythonExtensions REQUIRED)

add_subdirectory(hello)

#
# This code is here *ONLY* to test that the different signatures of
# "check_dynamic_lookup" functions are not causing errors.
#
include(targetLinkLibrariesWithDynamicLookup)
check_dynamic_lookup("MODULE" "SHARED" "HELLO_HAS_DYNAMIC_LOOKUP")
check_dynamic_lookup("HELLO_HAS_DYNAMIC_LOOKUP")
