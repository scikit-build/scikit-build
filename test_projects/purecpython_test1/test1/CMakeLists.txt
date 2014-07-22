cmake_minimum_required (VERSION 2.8.1 FATAL_ERROR)

project(test1)

#
# Use standard CMake package to find Python. This should be passed
# from PyCMake.
#

add_library(test1 MODULE test1.c)
SET_TARGET_PROPERTIES(test1 PROPERTIES PREFIX "")

INSTALL(TARGETS test1
  LIBRARY DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}
)

include_directories(${PYTHON_INCLUDE_DIRS})
target_link_libraries(test1 ${PYTHON_LIBRARIES})
