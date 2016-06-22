
add_cython_target(_hello CXX)
add_library(_hello MODULE ${_hello})
python_extension_module(_hello)

# for testing
file(COPY __init__.py DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
file(COPY __main__.py DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

add_test(NAME hello
         COMMAND ${PYTHON_EXECUTABLE} -m hello
         WORKING_DIRECTORY ${CMAKE_INSTALL_PREFIX})

install(TARGETS _hello LIBRARY DESTINATION hello)
install(FILES __init__.py      DESTINATION hello)
install(FILES __main__.py      DESTINATION hello)
