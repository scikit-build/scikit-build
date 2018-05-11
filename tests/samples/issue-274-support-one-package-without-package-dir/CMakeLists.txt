cmake_minimum_required(VERSION 3.5.0)

project(hello NONE)


set(module "${CMAKE_CURRENT_BINARY_DIR}/cmake_generated_module.py")
file(WRITE ${module} "# Generated from ${CMAKE_CURRENT_LIST_FILE}

def what():
    return \"cmake_generated_module\"

")
install(FILES ${module} DESTINATION hello/)
