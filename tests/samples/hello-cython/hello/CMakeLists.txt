
add_cython_target(_hello CXX)
add_library(_hello MODULE ${_hello})
python_extension_module(_hello)

install(TARGETS _hello LIBRARY DESTINATION hello)
