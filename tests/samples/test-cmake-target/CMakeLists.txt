cmake_minimum_required(VERSION 3.5.0)
project(test-cmake-target NONE)
file(WRITE "${CMAKE_BINARY_DIR}/foo.txt" "# foo")
file(WRITE "${CMAKE_BINARY_DIR}/runtime.txt" "# runtime")
install(FILES "${CMAKE_BINARY_DIR}/foo.txt" DESTINATION ".")
install(CODE "message(STATUS \"Project has been installed\")")
install(FILES "${CMAKE_BINARY_DIR}/runtime.txt" DESTINATION "." COMPONENT runtime)
install(CODE "message(STATUS \"Runtime component has been installed\")" COMPONENT runtime)
# Add custom target to only install component: runtime (libraries)
add_custom_target(install-runtime
    ${CMAKE_COMMAND}
    -DCMAKE_INSTALL_COMPONENT=runtime
    -P "${PROJECT_BINARY_DIR}/cmake_install.cmake"
    )
