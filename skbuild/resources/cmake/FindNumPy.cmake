#.rst:
# FindNumPy
#
# Find the include directory for numpy/arrayobject.h
#
# Result Variables
# ^^^^^^^^^^^^^^^^
#
# This module sets the following variables:
#
# ``NUMPY_FOUND``
# True, if the system has NumPy.
# ``NUMPY_INCLUDE_DIR``
# The directory with numpy/arrayobject.h

# handle the QUIETLY and REQUIRED arguments and set NUMPY_FOUND to TRUE if
# all listed variables are TRUE

if(NOT NUMPY_FOUND)
  find_package(PythonInterp)
  find_package(PythonLibs)

  if(PYTHON_EXECUTABLE)
    execute_process(COMMAND "${PYTHON_EXECUTABLE}"
      -c "import numpy; print(numpy.get_include())"
      OUTPUT_VARIABLE _numpy_include_dir
      OUTPUT_STRIP_TRAILING_WHITESPACE
      ERROR_QUIET
      )
  endif()
endif()

find_path(NUMPY_INCLUDE_DIR
  numpy/arrayobject.h
  PATHS "${_numpy_include_dir}" "${PYTHON_INCLUDE_DIR}"
  PATH_SUFFIXES numpy/core/include
  )

include(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(NUMPY
                                  REQUIRED_VARS NUMPY_INCLUDE_DIR
                                  )

mark_as_advanced(NUMPY_INCLUDE_DIR)
