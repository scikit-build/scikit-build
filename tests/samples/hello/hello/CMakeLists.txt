add_library(_hello MODULE _hello.cxx)
python_extension_module(_hello)

install(TARGETS _hello LIBRARY DESTINATION hello)
