#.rst:
#
# Find the include directory for numpy/arrayobject.h
#
# This module sets the following variables:
#
# ``NumPy_FOUND``
#   True if NumPy was found.
# ``NumPy_INCLUDE_DIR``
#   The include directories needed to use NumpPy.
# ``NumPy_VERSION``
#   The version of NumPy found.
# ``NumPy_CONV_TEMPLATE_EXECUTABLE``
#   The command-line arguments required to execute the conv-template script
# ``NumPy_FROM_TEMPLATE_EXECUTABLE``
#   The command-line arguments required to execute the from-template script
#
# The module will also explicitly define one cache variable:
#
# ``NumPy_INCLUDE_DIR``
#

if(NOT NumPy_FOUND)
  set(_find_extra_args)
  if(NumPy_FIND_REQUIRED)
    list(APPEND _find_extra_args REQUIRED)
  endif()
  if(NumPy_FIND_QUIET)
    list(APPEND _find_extra_args QUIET)
  endif()
  find_package(PythonInterp ${_find_extra_args})
  find_package(PythonLibs ${_find_extra_args})

  find_program(NumPy_CONV_TEMPLATE_EXECUTABLE NAMES conv-template)
  find_program(NumPy_FROM_TEMPLATE_EXECUTABLE NAMES from-template)

  if(PYTHON_EXECUTABLE)
    execute_process(COMMAND "${PYTHON_EXECUTABLE}"
      -c "import numpy; print(numpy.get_include())"
      OUTPUT_VARIABLE _numpy_include_dir
      OUTPUT_STRIP_TRAILING_WHITESPACE
      ERROR_QUIET
      )
    execute_process(COMMAND "${PYTHON_EXECUTABLE}"
      -c "import numpy; print(numpy.__version__)"
      OUTPUT_VARIABLE NumPy_VERSION
      OUTPUT_STRIP_TRAILING_WHITESPACE
      ERROR_QUIET
      )

    if(NOT NumPy_CONV_TEMPLATE_EXECUTABLE)
      execute_process(COMMAND "${PYTHON_EXECUTABLE}"
        -c "from numpy.distutils import conv_template; print(conv_template.__file__)"
        OUTPUT_VARIABLE _numpy_conv_template_file
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
        )
      set(NumPy_CONV_TEMPLATE_EXECUTABLE "${PYTHON_EXECUTABLE}" "${_numpy_conv_template_file}")
    endif()

    if(NOT NumPy_FROM_TEMPLATE_EXECUTABLE)
      execute_process(COMMAND "${PYTHON_EXECUTABLE}"
        -c "from numpy.distutils import from_template; print(from_template.__file__)"
        OUTPUT_VARIABLE _numpy_from_template_file
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
        )
      set(NumPy_FROM_TEMPLATE_EXECUTABLE "${PYTHON_EXECUTABLE}" "${_numpy_from_template_file}")
    endif()
  endif()
endif()

find_path(NumPy_INCLUDE_DIR
  numpy/arrayobject.h
  PATHS "${_numpy_include_dir}" "${PYTHON_INCLUDE_DIR}"
  PATH_SUFFIXES numpy/core/include
  )

set(NumPy_INCLUDE_DIRS ${NumPy_INCLUDE_DIR})

# handle the QUIETLY and REQUIRED arguments and set NumPy_FOUND to TRUE if
# all listed variables are TRUE
include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(NumPy
                                  REQUIRED_VARS NumPy_INCLUDE_DIR NumPy_CONV_TEMPLATE NumPy_FROM_TEMPLATE
                                  VERSION_VAR NumPy_VERSION
                                  )

mark_as_advanced(NumPy_INCLUDE_DIR)
