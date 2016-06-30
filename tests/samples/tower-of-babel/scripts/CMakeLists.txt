
add_cython_target(tbabel CXX EMBED_MAIN)

# generate modules header file
python_modules_header(modules)
include_directories(${modules_INCLUDE_DIRS})

# compile and link
get_property(MODS GLOBAL PROPERTY PY_LINKED_MODULES_LIST)
add_executable(tbabel ${tbabel})
target_link_libraries(tbabel ${MODS})
python_standalone_executable(tbabel)
add_test(NAME tbabel COMMAND tbabel)

set(_pp "")
set(_pp "${_pp}${CMAKE_SOURCE_DIR}")
set(_pp "${_pp}${PYTHON_PATH_SEPARATOR}")
set(_pp "${_pp}${CMAKE_BINARY_DIR}")

set_property(TEST tbabel PROPERTY ENVIRONMENT "PYTHONPATH=${_pp}")

install(TARGETS tbabel DESTINATION scripts)

