set(_module_name "_hello")
set(fortran_src_file "${CMAKE_CURRENT_SOURCE_DIR}/_hello.f90")

set(generated_module_file ${CMAKE_CURRENT_BINARY_DIR}/${_module_name}${PYTHON_EXTENSION_MODULE_SUFFIX})

add_f2py_target(${_module_name} "${fortran_src_file}" OUTPUT_VAR _module_target_output)

add_library(${_module_name} MODULE ${_module_name})
target_include_directories(${_module_name} PRIVATE ${F2PY_INCLUDE_DIRS})
target_link_libraries(${_module_name} ${F2PY_LIBRARIES})
python_extension_module(${_module_name})

install(TARGETS ${_module_name}
  LIBRARY DESTINATION hello
)
