# Setup basic python stuff and ensure we have skbuild

option(BUILD_MYALGO "Enable _myalgo_cython module" TRUE)
if (BUILD_MYALGO)

  set(cython_source "_myalgo_cython.pyx")
  set(MYALGO_MODULE_NAME "_myalgo_cython")

  # Translate Cython into C/C++
  add_cython_target(${MYALGO_MODULE_NAME} "${cython_source}" C OUTPUT_VAR sources)

  # Add other C sources
  list(APPEND sources )

  # Create C++ library. Specify include dirs and link libs as normal
  add_library(${MYALGO_MODULE_NAME} MODULE ${sources})
  target_include_directories(
    ${MYALGO_MODULE_NAME}
    PUBLIC
        ${NumPy_INCLUDE_DIRS}
        ${PYTHON_INCLUDE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}
  )

  # TODO: not sure why this isn't set in the global scope?
  # Hack around it: just hard code the module name
  set(MECL_MODULE_NAME "mecl")

  # TODO: linking to the SCCD shared object isn't working 100% yet.
  target_link_libraries(${MYALGO_MODULE_NAME} ${MECL_MODULE_NAME})

  target_compile_definitions(${MYALGO_MODULE_NAME} PUBLIC
    "NPY_NO_DEPRECATED_API"
    #"NPY_1_7_API_VERSION=0x00000007"
    )

  # Transform the C++ library into an importable python module
  python_extension_module(${MYALGO_MODULE_NAME})

  # My "normal" method of setting install targets does not seem to work here. Hacking it.
  # NOTE: skbuild *seems* to place libraries in a data dir *unless* the install destination
  # corresponds exactly to the <package_dir>/<package_name> specified implicitly in setup.py
  set(my_skb_mod_install_dest "src/python/my_skb_mod")

  install(TARGETS ${MYALGO_MODULE_NAME} LIBRARY DESTINATION "${my_skb_mod_install_dest}")

endif()
