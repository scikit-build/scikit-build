set(world "${CMAKE_CURRENT_SOURCE_DIR}/world.py")
file(WRITE ${world} "")

install(FILES ${world} DESTINATION hello)
