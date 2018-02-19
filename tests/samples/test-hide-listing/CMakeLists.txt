cmake_minimum_required(VERSION 3.5.0)

project(test_hide_listing NONE)

add_subdirectory(hello)

file(WRITE "${CMAKE_BINARY_DIR}/helloModule.py" "# helloModule.py")
install(FILES "${CMAKE_BINARY_DIR}/helloModule.py" DESTINATION ".")
