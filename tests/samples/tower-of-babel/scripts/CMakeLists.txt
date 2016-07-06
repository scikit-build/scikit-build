
add_cython_target(tbabel CXX EMBED_MAIN)

# generate modules header file
python_modules_header(modules)
include_directories(${modules_INCLUDE_DIRS})

# compile and link
get_property(MODS GLOBAL PROPERTY PY_LINKED_MODULES_LIST)
add_executable(tbabel ${tbabel})
target_link_libraries(tbabel ${MODS})
python_standalone_executable(tbabel)

add_test(NAME tbabel COMMAND tbabel
         WORKING_DIRECTORY ${CMAKE_BUILD_DIRECTORY})

set_property(TEST tbabel PROPERTY ENVIRONMENT
             "LD_LIBRARY_PATH=${CMAKE_BUILD_DIRECTORY};DYLD_LIBRARY_PATH=${CMAKE_BUILD_DIRECTORY}")

install(TARGETS tbabel DESTINATION scripts)
