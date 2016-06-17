cmake_minimum_required(VERSION 3.5.0)

project(fail_outside_project_root)

set(CMAKE_MODULE_PATH
    ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/../cmake-files)

install(FILES dummy DESTINATION ..)

