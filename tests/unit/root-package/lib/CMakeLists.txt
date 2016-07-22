add_library(_spam MODULE _spam.c)
python_extension_module(_spam)

add_test(NAME spam
         COMMAND ${PYTHON_EXECUTABLE} -m spam
         WORKING_DIRECTORY ${CMAKE_INSTALL_PREFIX})

install(TARGETS _spam LIBRARY DESTINATION "lib")
install(FILES spam.py         DESTINATION "lib")
