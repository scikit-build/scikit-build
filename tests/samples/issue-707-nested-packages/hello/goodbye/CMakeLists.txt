add_cython_target(_goodbye CXX)
add_library(_goodbye MODULE ${_goodbye})
python_extension_module(_goodbye)

install(TARGETS _goodbye LIBRARY DESTINATION hello/goodbye)
