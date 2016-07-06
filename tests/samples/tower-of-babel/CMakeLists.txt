cmake_minimum_required(VERSION 3.5.0)

project(tower_of_babel)

include(CTest)
enable_testing()

set(CMAKE_MODULE_PATH
    ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/../cmake-files)

find_package(PythonInterp REQUIRED)
find_package(PythonLibs REQUIRED)
find_package(PythonExtensions REQUIRED)
find_package(Cython REQUIRED)
find_package(Boost COMPONENTS python)


include_directories(${CMAKE_CURRENT_SOURCE_DIR})

add_cython_target(tbabel_cython_static CXX)
add_cython_target(tbabel_cython_shared CXX)
add_cython_target(tbabel_cython_module CXX)


add_library(tbabel_cython_static STATIC ${tbabel_cython_static})
add_library(tbabel_cython_shared SHARED ${tbabel_cython_shared})
add_library(tbabel_cython_module MODULE ${tbabel_cython_module})


include_directories(${Boost_INCLUDE_DIRS})


add_library(tbabel_boost_static STATIC tbabel_boost_static.cxx)
add_library(tbabel_boost_shared SHARED tbabel_boost_shared.cxx)
add_library(tbabel_boost_module MODULE tbabel_boost_module.cxx)

target_link_libraries(tbabel_boost_static ${Boost_LIBRARIES})
target_link_libraries(tbabel_boost_shared ${Boost_LIBRARIES})
target_link_libraries(tbabel_boost_module ${Boost_LIBRARIES})


python_extension_module(tbabel_cython_static)
python_extension_module(tbabel_cython_shared)
python_extension_module(tbabel_cython_module)

python_extension_module(tbabel_boost_static)
python_extension_module(tbabel_boost_shared)
python_extension_module(tbabel_boost_module)

set(site_packages "${PYTHON_RELATIVE_SITE_PACKAGES_DIR}")

install(TARGETS tbabel_cython_static DESTINATION lib)
install(TARGETS tbabel_cython_shared DESTINATION lib)
install(TARGETS tbabel_cython_module DESTINATION ${site_packages})

install(TARGETS tbabel_boost_static DESTINATION lib)
install(TARGETS tbabel_boost_shared DESTINATION lib)
install(TARGETS tbabel_boost_module DESTINATION ${site_packages})


install(FILES tbabel_cython_static.pxd DESTINATION ${site_packages})
install(FILES tbabel_cython_shared.pxd DESTINATION ${site_packages})
install(FILES tbabel_cython_module.pxd DESTINATION ${site_packages})

install(FILES tbabel_cython_common.pxi DESTINATION ${site_packages})


install(FILES tbabel_boost_static.h DESTINATION include)
install(FILES tbabel_boost_shared.h DESTINATION include)
install(FILES tbabel_boost_module.h DESTINATION include)

install(FILES tbabel_boost_common.h DESTINATION include)

install(FILES tbabel_python.py DESTINATION ${site_packages})

file(COPY tbabel_python.py DESTINATION ${CMAKE_BINARY_DIR})

add_subdirectory(scripts)

