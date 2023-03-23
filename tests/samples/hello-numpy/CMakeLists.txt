cmake_minimum_required(VERSION 3.18...3.22)

project(hello-numpy VERSION "0.1")

# Define CMAKE_INSTALL_xxx: LIBDIR, INCLUDEDIR
include(GNUInstallDirs)

find_package(Python REQUIRED COMPONENTS Development NumPy)

# Fetch pybind11
include(FetchContent)

FetchContent_Declare(
  pybind11
  URL https://github.com/pybind/pybind11/archive/refs/tags/v2.10.0.tar.gz
  URL_HASH SHA256=eacf582fa8f696227988d08cfc46121770823839fe9e301a20fbce67e7cd70ec
)
FetchContent_MakeAvailable(pybind11)

set(python_module_name _hello)
pybind11_add_module(${python_module_name} MODULE
  src/hello/hello_py.cpp
  )

target_link_libraries(
  ${python_module_name}
  PUBLIC Python::NumPy
         pybind11::module
)

target_compile_definitions(${python_module_name}
                           PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO})

install(TARGETS ${python_module_name} DESTINATION .)
