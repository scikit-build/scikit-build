
# Use .pyd extension on all platforms. This will avoid failure
# on macOS where wheel wheel/macosx_libfile.py attempts to extract
# shared library information.

file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/swig_mwe.py" "")
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/_swig_mwe.pyd" "")

install(FILES
    ${CMAKE_CURRENT_BINARY_DIR}/swig_mwe.py
    ${CMAKE_CURRENT_BINARY_DIR}/_swig_mwe.pyd
  DESTINATION hello
  )
