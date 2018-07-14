# Include python
find_package(PythonInterp REQUIRED)
find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_PATH})

# load SWIG macros. The path to UseSWIG.cmake is provided by SWIG_USE_FILE which is set in FindSWIG
if (SWIG_USE_FILE STREQUAL "")
  message(FATAL_ERROR "unexpected: the variable SWIG_USE_FILE is the empty string. Did you run FindSWIG.cmake?")
else()
  include(${SWIG_USE_FILE})
endif()

# Add swig module
list(APPEND CMAKE_SWIG_FLAGS -v -O)
include_directories(../..)
set_source_files_properties(../swig-mwe.i PROPERTIES CPLUSPLUS ON)
swig_add_library(swig_mwe LANGUAGE python SOURCES ../swig-mwe.i)
swig_link_libraries(swig_mwe ${PYTHON_LIBRARIES} foo)

# Files to install with Python
set(PYTHON_INSTALL_FILES ${CMAKE_CURRENT_BINARY_DIR}/swig_mwe.py)
if(UNIX)
  list(APPEND PYTHON_INSTALL_FILES ${CMAKE_CURRENT_BINARY_DIR}/_swig_mwe.so)
endif()

if(NOT DEFINED PYTHON_REL_SITE_ARCH)
  execute_process(COMMAND ${PYTHON_EXECUTABLE} "-c" "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))"
                  OUTPUT_VARIABLE PYTHON_SITE_ARCH
                  RESULT_VARIABLE PYTHON_SITEARCH_NOT_FOUND)
  #extract correctly python location: e.g lib64/python2.7/site-packages
  string(REGEX MATCH "[Ll]ib.*packages" PYTHON_REL_SITE_ARCH ${PYTHON_SITE_ARCH})
endif()

install(FILES ${PYTHON_INSTALL_FILES}
        DESTINATION ${PYTHON_REL_SITE_ARCH}
        PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ)

if(BUILD_TESTING)
  add_test(NAME test_python COMMAND "${PYTHON_EXECUTABLE}" ${CMAKE_CURRENT_SOURCE_DIR}/test.py)
  if (MSVC)
  set_tests_properties ( test_python PROPERTIES ENVIRONMENT "PYTHONPATH=${CMAKE_CURRENT_BINARY_DIR}/Release\;${CMAKE_CURRENT_BINARY_DIR}")
  else()
  set_tests_properties ( test_python PROPERTIES ENVIRONMENT "PYTHONPATH=${CMAKE_CURRENT_BINARY_DIR}")
  endif(MSVC)
endif(BUILD_TESTING)


