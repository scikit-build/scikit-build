cmake_minimum_required(VERSION 3.5...3.26)
project(hello_cid NONE)
file(WRITE "${CMAKE_BINARY_DIR}/hello_cid.h" "#define HELLO_ANSWER 42\n")
install(FILES "${CMAKE_BINARY_DIR}/hello_cid.h" DESTINATION include)
