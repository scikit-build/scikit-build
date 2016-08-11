add_library(_hello MODULE _hello.cxx)
python_extension_module(_hello)

add_test(NAME hello
         COMMAND ${PYTHON_EXECUTABLE} -m hello
         WORKING_DIRECTORY ${CMAKE_INSTALL_PREFIX})

install(TARGETS _hello LIBRARY DESTINATION "lib")
install(FILES hello.py         DESTINATION "lib")
