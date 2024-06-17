cmake_minimum_required(VERSION 3.5)

project(hello NONE)

# Headers
file(WRITE "bar.h" "")
file(WRITE "foo.h" "")
install(FILES "bar.h" "foo.h" DESTINATION include)

# Static libraries
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/libbar.a" "")
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/libfoo.a" "")
install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/libbar.a"
    "${CMAKE_CURRENT_BINARY_DIR}/libfoo.a"
  DESTINATION lib/static
  )

# Executables
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/hello" "")
install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/hello"
  DESTINATION bin
  )

add_subdirectory(wrapping/python)
