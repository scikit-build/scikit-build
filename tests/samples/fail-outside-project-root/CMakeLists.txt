cmake_minimum_required(VERSION 3.5.0)

project(fail_outside_project_root NONE)

install(CODE "execute_process(COMMAND \${CMAKE_COMMAND} -E sleep 0)")

if(INSTALL_FILE)
  install(FILES dummy DESTINATION ..)
endif()

if(INSTALL_PROJECT)

  set(other_project_source_dir ${CMAKE_SOURCE_DIR}/other_project)
  set(other_project_build_dir ${CMAKE_BINARY_DIR}/../other_project-build)
  set(other_project_install_dir ${CMAKE_BINARY_DIR}/../other_project-install)

  file(MAKE_DIRECTORY ${other_project_build_dir})

  # Configure
  execute_process(
    COMMAND ${CMAKE_COMMAND}
      ${other_project_source_dir}
    WORKING_DIRECTORY ${other_project_build_dir}
    )

  # Install other_project
  install(CODE "
set(CMAKE_INSTALL_PREFIX \"${other_project_install_dir}\")
include(\"${other_project_build_dir}/cmake_install.cmake\")
")

endif()
