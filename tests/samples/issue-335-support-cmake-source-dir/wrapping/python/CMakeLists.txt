file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/swig_mwe.py" "")
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/_swig_mwe.so" "")

install(FILES
    ${CMAKE_CURRENT_BINARY_DIR}/swig_mwe.py
    ${CMAKE_CURRENT_BINARY_DIR}/_swig_mwe.so
  DESTINATION hello
  )
