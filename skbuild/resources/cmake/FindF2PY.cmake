#.rst:
#
# The purpose of the F2PY –Fortran to Python interface generator– project is to provide a
# connection between Python and Fortran languages.
#
# F2PY is a Python package (with a command line tool f2py and a module f2py2e) that facilitates
# creating/building Python C/API extension modules that make it possible to call Fortran 77/90/95
# external subroutines and Fortran 90/95 module subroutines as well as C functions; to access Fortran
# 77 COMMON blocks and Fortran 90/95 module data, including allocatable arrays from Python.
#
# For more information on the F2PY project, see http://www.f2py.com/.
#
# The following variables are defined:
# ::
#
#   F2PY_EXECUTABLE                     - absolute path to the F2PY executable
#                                         
#   F2PY_VERSION                        - the F2PY version
#
#   F2PY_VERSION_MAJOR                  - the F2PY major version
#
#   F2PY_VERSION_MINOR                  - the F2PY minor version
#
#   F2PY_VERSION_MICRO                  - the F2PY micro version
#
#
# By default, the module finds the F2PY program that is shipped with NumPy.
#
# Example usage
# ^^^^^^^^^^^^^
#
# .. code-block:: cmake
#
#   add_custom_target(fortran_methods ALL
#     DEPENDS fortran_methods${CMAKE_SHARED_LIBRARY_SUFFIX}
#     )
#   add_custom_command(OUTPUT fortran_methodsmodule.c
#     COMMAND ${F2PY_EXECUTABLE} -m fortran_methods
#             -I${PROJECT_BINARY_DIR}/src
#             --f90flags="-fdefault-real-8"
#             ${PROJECT_SOURCE_DIR}/src/fortran_methods/main.f90
#    )
#
#=============================================================================
# Copyright 2011-2017, the PyNE Development Team. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
# 
#    1. Redistributions of source code must retain the above copyright notice, this list of
#       conditions and the following disclaimer.
# 
#    2. Redistributions in binary form must reproduce the above copyright notice, this list
#       of conditions and the following disclaimer in the documentation and/or other materials
#       provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE PYNE DEVELOPMENT TEAM ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# The views and conclusions contained in the software and documentation are those of the
# authors and should not be interpreted as representing official policies, either expressed
# or implied, of the stakeholders of the PyNE project or the employers of PyNE developers.
#=============================================================================

find_package(NumPy)

find_program(F2PY_EXECUTABLE F2PY ${DEPS_BIN_HINTS})
if(NOT F2PY_EXECUTABLE)
  if(${PYTHON_VERSION_MAJOR} GREATER 2)
    find_program(F2PY_EXECUTABLE3 F2PY3 ${DEPS_BIN_HINTS})
    if(F2PY_EXECUTABLE3)
      set(F2PY_EXECUTABLE ${F2PY_EXECUTABLE3})
    endif()
  elseif(${PYTHON_VERSION_MAJOR} LESS 3)
    # because arch is dumb
    find_program(F2PY_EXECUTABLE2 F2PY2 ${DEPS_BIN_HINTS})
    if(F2PY_EXECUTABLE2)
      set(F2PY_EXECUTABLE ${F2PY_EXECUTABLE2})
    endif()
  endif()
endif()

if(F2PY_EXECUTABLE)
  set(F2PY_FOUND TRUE)

  # get the version string
  execute_process(COMMAND "${F2PY_EXECUTABLE}" "-v"
                  OUTPUT_VARIABLE F2PY_VERSION_RTN
                  OUTPUT_STRIP_TRAILING_WHITESPACE)
  string(REPLACE " " ";" F2PY_VERSION_RTN_LIST ${F2PY_VERSION_RTN})
  list(GET F2PY_VERSION_RTN_LIST -1 F2PY_VERSION)
  string(REPLACE "." ";" F2PY_VERSION_LIST ${F2PY_VERSION})
  list(LENGTH F2PY_VERSION_LIST F2PY_VERSION_N)
  list(GET F2PY_VERSION_LIST 0 F2PY_VERSION_MAJOR)
  if(F2PY_VERSION_N GREATER 1)
    list(GET F2PY_VERSION_LIST 1 F2PY_VERSION_MINOR)
  else(F2PY_VERSION_N GREATER 1)
    set(F2PY_VERSION_MINOR 0)
  endif()
  if(F2PY_VERSION_N GREATER 2)
    list(GET F2PY_VERSION_LIST 2 F2PY_VERSION_MICRO)
  else(F2PY_VERSION_N GREATER 2)
    set(F2PY_VERSION_MICRO 0)
  endif()
else()
  set(F2PY_FOUND FALSE)
endif()

include(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(F2PY REQUIRED_VARS F2PY_EXECUTABLE)

mark_as_advanced(F2PY_EXECUTABLE)
