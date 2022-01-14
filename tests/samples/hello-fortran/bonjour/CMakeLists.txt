set(_module_name _bonjour)

add_f2py_target(_bonjour
  "${CMAKE_CURRENT_SOURCE_DIR}/_bonjour.pyf"
  OUTPUT_VAR _pyf_target_output
  )

add_library(${_module_name} MODULE ${_module_name})
target_include_directories(${_module_name} PRIVATE ${F2PY_INCLUDE_DIRS})
target_link_libraries(${_module_name} ${F2PY_LIBRARIES})
python_extension_module(${_module_name})

install(TARGETS ${_module_name}
  LIBRARY DESTINATION hello
)
