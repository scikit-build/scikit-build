cmake_minimum_required(VERSION 3.2)

project(mwe CXX)

set(CMAKE_CXX_STANDARD 11)

if (UNIX)
  list(APPEND CMAKE_CXX_FLAGS  "-Wall -Wextra -Wno-unused-parameter -fPIC")
endif()

set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)

include (CTest)

# Create bar library
add_library(bar bar.cpp)
set_target_properties(bar PROPERTIES PUBLIC_HEADER "bar.h")

# Create foo library that links to bar
add_library(foo foo.cpp)
target_link_libraries(foo bar)
set_target_properties(foo PROPERTIES PUBLIC_HEADER "foo.h")

# Create C++ stand alone executable calling foo and bar
add_executable(hello main.cpp)
target_link_libraries(hello foo)

enable_testing ()
# Add the SWIG wrappers
add_subdirectory(swig)

# Add install target
install(TARGETS hello foo bar
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib/static
        PUBLIC_HEADER DESTINATION include)

# Test the C++ hello binary
add_test( NAME test_hello COMMAND hello)
set_tests_properties (test_hello PROPERTIES
        PASS_REGULAR_EXPRESSION "^Hello from main\nHello from foo\nHello from bar\n$")
