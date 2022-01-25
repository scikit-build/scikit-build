cmake_minimum_required(VERSION 3.14...3.18)

project(hello-pybind11 VERSION "0.1")

# Define CMAKE_INSTALL_xxx: LIBDIR, INCLUDEDIR
include(GNUInstallDirs)

# Fetch pybind11
include(FetchContent)

FetchContent_Declare(
  pybind11
  URL https://github.com/pybind/pybind11/archive/refs/tags/v2.6.2.tar.gz
  URL_HASH SHA256=8ff2fff22df038f5cd02cea8af56622bc67f5b64534f1b83b9f133b8366acff2
)
FetchContent_MakeAvailable(pybind11)

set(python_module_name _hello)
pybind11_add_module(${python_module_name} MODULE
  src/hello/hello_py.cpp
  )

install(TARGETS ${python_module_name} DESTINATION .)

# Quiet a warning, since this project is only valid with SKBUILD
set(ignoreMe "${SKBUILD}")
