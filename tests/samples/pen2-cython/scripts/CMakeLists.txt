
install(FILES pen2_cython DESTINATION scripts)
file(COPY pen2_cython DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

add_test(NAME pen2_cython
         COMMAND ${PYTHON_EXECUTABLE}
                 "${CMAKE_INSTALL_PREFIX}/scripts/pen2_cython" -d 2)
set_property(TEST pen2_cython PROPERTY ENVIRONMENT
  "PYTHONPATH=${CMAKE_SOURCE_DIR}/src${PYTHON_PATH_SEPARATOR}${CMAKE_BINARY_DIR}")


