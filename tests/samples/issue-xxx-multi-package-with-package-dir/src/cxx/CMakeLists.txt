# TODO: Can we make this work in either shared or static mode?

option(BUILD_MECL "Enable MECL (my extern c lib) library" TRUE)
if (BUILD_MECL)

  set(THREADS_PREFER_PTHREAD_FLAG ON)

  # TODO: include external deps in mecl

  # Find required external libraries
  find_package(Threads REQUIRED)
  #find_package(ZLIB REQUIRED)
  #find_package(GSL REQUIRED)
  #find_package(OpenMP)

  # Corresponds to FFLAGS
  #set (CMAKE_Fortran_FLAGS "${CMAKE_Fortran_FLAGS} -g -fPIC")

  # Hacks:
  #set (CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fPIC")

  #add_library(GLMnet STATIC "GLMnet.f")

  set(MECL_MODULE_NAME "mecl")
  # Add other C sources
  list(APPEND mecl_sources "my_extern_clib.c")
  ## Create C++ library. Specify include dirs and link libs as normal
  #add_library(${MECL_MODULE_NAME} SHARED ${mecl_sources})

  # HACK: statically link the library to the cython module because
  # I'm having trouble making the shared library work.
  add_library(${MECL_MODULE_NAME} STATIC ${mecl_sources})

  #target_include_directories(
  #  ${MECL_MODULE_NAME}
  #  PUBLIC
  #      ${NumPy_INCLUDE_DIRS}
  #      ${PYTHON_INCLUDE_DIRS}
  #      ${CMAKE_CURRENT_SOURCE_DIR}
  #)

  #message(STATUS "OpenMP::OpenMP_C = ${OpenMP::OpenMP_C}")
  #message(STATUS "ZLIB::ZLIB = ${ZLIB::ZLIB}")
  #message(STATUS "Threads::Threads = ${Threads::Threads}")
  message(STATUS "Threads = ${Threads}")

  target_link_libraries(
    ${MECL_MODULE_NAME} PUBLIC
    #ZLIB::ZLIB
    Threads::Threads
  )

  #target_compile_definitions(${SCCD_MODULE_NAME} PUBLIC
  #  "NPY_NO_DEPRECATED_API"
  #  #"NPY_1_7_API_VERSION=0x00000007"
  #  )

  # Transform the C++ library into an importable python module
  #python_extension_module(${SCCD_MODULE_NAME})

  # Install the C++ module to the correct relative location
  # (this will be an inplace build if you use `pip install -e`)
  #file(RELATIVE_PATH _install_dest "${CMAKE_SOURCE_DIR}" "${CMAKE_CURRENT_SOURCE_DIR}")
  # Is this right?
  #install(TARGETS ${SCCD_MODULE_NAME} LIBRARY DESTINATION "${_install_dest}../tool/python/pycold")

endif()
