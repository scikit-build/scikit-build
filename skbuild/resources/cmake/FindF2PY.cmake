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
#
# ::
#
#   F2PY_EXECUTABLE      - absolute path to the F2PY executable
#
# ::
#
#   F2PY_VERSION_STRING  - the version of F2PY found
#   F2PY_VERSION_MAJOR   - the F2PY major version
#   F2PY_VERSION_MINOR   - the F2PY minor version
#   F2PY_VERSION_PATCH   - the F2PY patch version
#
#
# .. note::
#
#   By default, the module finds the F2PY program associated with the installed NumPy package.
#
# Example usage
# ^^^^^^^^^^^^^
#
# Assuming that a package named ``method`` is declared in ``setup.py`` and that the corresponding directory
# containing ``__init__.py`` also exists, the following CMake code can be added to ``method/CMakeLists.txt``
# to ensure the C sources associated with ``cylinder_methods.f90`` are generated and the corresponding module
# is compiled:
#
# .. code-block:: cmake
#
#   find_package(F2PY REQUIRED)
#
#   set(f2py_module_name "_cylinder_methods")
#   set(fortran_src_file "${CMAKE_CURRENT_SOURCE_DIR}/cylinder_methods.f90")
#
#   set(generated_module_file ${CMAKE_CURRENT_BINARY_DIR}/${f2py_module_name}${PYTHON_EXTENSION_MODULE_SUFFIX})
#
#   add_custom_target(${f2py_module_name} ALL
#     DEPENDS ${generated_module_file}
#     )
#
#   add_custom_command(
#     OUTPUT ${generated_module_file}
#     COMMAND ${F2PY_EXECUTABLE}
#       -m ${f2py_module_name}
#       -c
#       ${fortran_src_file}
#     WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
#     )
#
#   install(FILES ${generated_module_file} DESTINATION methods)
#
# .. warning::
#
#   Using ``f2py`` with ``-c`` argument means that f2py is also responsible to build the module. In that
#   case, CMake is not used to find the compiler and configure the associated build system.
#

find_program(F2PY_EXECUTABLE NAMES f2py f2py${PYTHON_VERSION_MAJOR})

if(F2PY_EXECUTABLE)
  # extract the version string
  execute_process(COMMAND "${F2PY_EXECUTABLE}" -v
                  OUTPUT_VARIABLE F2PY_VERSION_STRING
                  OUTPUT_STRIP_TRAILING_WHITESPACE)
  if("${F2PY_VERSION_STRING}" MATCHES "^([0-9]+)(.([0-9+]))?(.([0-9+]))?$")
    set(F2PY_VERSION_MAJOR ${CMAKE_MATCH_1})
    set(F2PY_VERSION_MINOR "${CMAKE_MATCH_3}")
    set(F2PY_VERSION_PATCH "${CMAKE_MATCH_5}")
  endif()
endif()

# handle the QUIETLY and REQUIRED arguments and set F2PY_FOUND to TRUE if
# all listed variables are TRUE
include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(F2PY
  REQUIRED_VARS F2PY_EXECUTABLE
  VERSION_VAR F2PY_VERSION_STRING
  )

mark_as_advanced(F2PY_EXECUTABLE)
