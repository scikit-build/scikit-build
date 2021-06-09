add_library(_hello MODULE _hello.cxx)
python_extension_module(_hello)

install(TARGETS _hello LIBRARY DESTINATION hello)

set(world "${CMAKE_CURRENT_SOURCE_DIR}/world.py")
file(WRITE ${world} "")

install(FILES ${world} DESTINATION hello)
