#
# - This module provides the function
# target_link_libraries_with_dynamic_lookup which can be used to
# "weakly" link loadable module.
#
# Link a library to a target such that the symbols are resolved at
# run-time not link-time. This should be used when compiling a
# loadable module when the symbols should be resolve from the run-time
# environment where the module is loaded, and not a specific system
# library.
#
# Specifically, for OSX it uses undefined dynamic_lookup. This is
# similar to using "-shared" on Linux where undefined symbols are
# ignored.
#
# Additionally, the linker is checked to see if it supports undefined
# symbols when linking a shared library. If it does then the library
# is not linked when specified with this function.
#
# http://blog.tim-smith.us/2015/09/python-extension-modules-os-x/
#
#
# The following functions are defined:
#
#   has_dynamic_lookup(<ResultVar>)
#
# Check if the linker requires a command line flag to allow leaving symbols
# unresolved until runtime.  A test project is built and ran and ``<ResultVar>``
# is set based on whether the project was built and ran successfully.  The
# result is cached between invocations and recomputed only when the value of
# ``CMAKE_SHARED_LINKER_FLAGS`` changes.
#
# Defined variables:
#
# ``<ResultVar>``
#   Whether the linker allows undefined symbols for shared libraries.
#
# ``HAS_DYNAMIC_LOOKUP``
#   Cached alias.
#
#
#   has_symbol_dedupe(<ResultVar>)
#
# Check if the linker/loader correctly coalesces symbols that have been
# duplicated across link boundaries.  A test project is built and ran and
# ``<ResultVar>`` is set based on whether the project was built and ran
# successfully.  The result is cached between invocations and recomputed only
# when the value of ``CMAKE_SHARED_LINKER_FLAGS`` changes.

# Defined variables:
#
# ``<ResultVar>``
#   Whether the linker/loader correctly coalesces duplicated symbols
#
# ``HAS_SYMBOL_DEDUPE``
#   Cached alias.
#

function(_test_weak_link_project projectName testName)
  set(options DYNAMIC_LOOKUP SYMBOL_DEDUPE)
  cmake_parse_arguments(_args "${options}" "" "" ${ARGN})

  set(test_project_src_dir
      "${PROJECT_BINARY_DIR}/CMakeTmp/${projectName}/src")
  set(test_project_bin_dir
      "${PROJECT_BINARY_DIR}/CMakeTmp/${projectName}/build")

  file(MAKE_DIRECTORY ${test_project_src_dir})
  file(MAKE_DIRECTORY ${test_project_bin_dir})

  file(WRITE "${test_project_src_dir}/CMakeLists.txt" "
    cmake_minimum_required(VERSION ${CMAKE_VERSION})
    project(${projectName} C)

    include_directories(${test_project_src_dir})

    add_library(number SHARED number.c)

    add_library(counter MODULE counter.c)
    set_target_properties(counter PROPERTIES PREFIX \"\")
  ")

  if(_args_DYNAMIC_LOOKUP)
    file(APPEND "${test_project_src_dir}/CMakeLists.txt" "
    set_target_properties(
      counter
      PROPERTIES LINK_FLAGS \"-undefined dynamic_lookup\")
    ")
  elseif(_args_SYMBOL_DEDUPE)
    file(APPEND "${test_project_src_dir}/CMakeLists.txt" "
    target_link_libraries(counter number)
    ")
  endif()

  file(APPEND "${test_project_src_dir}/CMakeLists.txt" "
    add_executable(main main.c)
    target_link_libraries(main number)
    target_link_libraries(main ${CMAKE_DL_LIBS})
  ")

  file(WRITE "${test_project_src_dir}/number.c" "
    #include <number.h>

    static int _number;
    void set_number(int number) { _number = number; }
    int get_number() { return _number; }
  ")

  file(WRITE "${test_project_src_dir}/number.h" "
    #ifndef _NUMBER_H
    #define _NUMBER_H
    extern void set_number(int);
    extern int get_number(void);
    #endif
  ")

  file(WRITE "${test_project_src_dir}/counter.c" "
    #include <number.h>
    int count() {
      int result = get_number();
      set_number(result + 1);
      return result;
    }
  ")

  file(WRITE "${test_project_src_dir}/counter.h" "
    #ifndef _COUNTER_H
    #define _COUNTER_H
    extern int count(void);
    #endif
  ")

  file(WRITE "${test_project_src_dir}/main.c" "
    #include <stdlib.h>
    #include <stdio.h>
    #include <dlfcn.h>

    int my_count() {
      int result = get_number();
      set_number(result + 1);
      return result;
    }

    int main(int argc, char **argv) {
      void *counter_module;
      int (*count)(void);
      int result;

      counter_module = dlopen(\"./counter.so\", RTLD_LAZY);
      if(!counter_module) goto error;

      count = dlsym(counter_module, \"count\");
      if(!count) goto error;

      result = count()    != 0 ? 1 :
               my_count() != 1 ? 1 :
               my_count() != 2 ? 1 :
               count()    != 3 ? 1 :
               count()    != 4 ? 1 :
               count()    != 5 ? 1 :
               my_count() != 6 ? 1 : 0;


      goto done;
      error:
        fprintf(stderr, \"Error occured:\\n    %s\\n\", dlerror());
        result = 1;

      done:
        if(counter_module) dlclose(counter_module);
        return result;
    }
  ")

  set(_rpath_arg)
  if(APPLE AND ${CMAKE_VERSION} VERSION_GREATER 2.8.11)
    set(_rpath_arg "-DCMAKE_MACOSX_RPATH='${CMAKE_MACOSX_RPATH}'")
  endif()

  try_compile(project_compiles
              "${test_project_bin_dir}"
              "${test_project_src_dir}"
              "${projectName}"
              CMAKE_FLAGS
                "-DCMAKE_SHARED_LINKER_FLAGS='${CMAKE_SHARED_LINKER_FLAGS}'"
                ${_rpath_arg}
              OUTPUT_VARIABLE compile_output)

  set(project_works 1)
  set(run_output)

  if(project_compiles)
    execute_process(COMMAND "${test_project_bin_dir}/main"
                    WORKING_DIRECTORY "${test_project_bin_dir}"
                    RESULT_VARIABLE project_works
                    OUTPUT_VARIABLE run_output
                    ERROR_VARIABLE run_output)
  endif()

  if(project_works EQUAL 0)
    set(project_works TRUE)
    message(STATUS "Performing Test ${testName} - Success")
  else()
    set(project_works FALSE)
    message(STATUS "Performing Test ${testName} - Failed")
    file(APPEND ${CMAKE_BINARY_DIR}/${CMAKE_FILES_DIRECTORY}/CMakeError.log
         "Performing Test ${testName} failed with the following output:\n"
         "BUILD\n-----\n${compile_output}\nRUN\n---\n${run_output}\n")
  endif()

  set(${projectName} ${project_works} PARENT_SCOPE)
endfunction()


function(has_dynamic_lookup resultVar)
  # hash the CMAKE_FLAGS passed and check cache to know if we need to rerun
  string(MD5 cmake_flags_hash "${CMAKE_SHARED_LINKER_FLAGS}")

  if(     NOT DEFINED HAS_DYNAMIC_LOOKUP_hash
       OR NOT "${HAS_DYNAMIC_LOOKUP_hash}" STREQUAL "${cmake_flags_hash}")
    unset(HAS_DYNAMIC_LOOKUP)
  endif()

  if(NOT DEFINED HAS_DYNAMIC_LOOKUP)
    _test_weak_link_project(has_dynamic_lookup
                            HAS_DYNAMIC_LOOKUP
                            DYNAMIC_LOOKUP)

    set(HAS_DYNAMIC_LOOKUP ${has_dynamic_lookup}
        CACHE BOOL "linker requires \"dynamic_lookup\" for undefined symbols")

    set(HAS_DYNAMIC_LOOKUP_hash "${cmake_flags_hash}"
        CACHE INTERNAL "hashed flags for HAS_DYNAMIC_LOOKUP check")
  endif()

  set(${resultVar} "${HAS_DYNAMIC_LOOKUP}" PARENT_SCOPE)
endfunction()


function(has_symbol_dedupe resultVar)
  # hash the CMAKE_FLAGS passed and check cache to know if we need to rerun
  string(MD5 cmake_flags_hash "${CMAKE_SHARED_LINKER_FLAGS}")

  if(     NOT DEFINED HAS_SYMBOL_DEDUPE_hash
       OR NOT "${HAS_SYMBOL_DEDUPE_hash}" STREQUAL "${cmake_flags_hash}")
    unset(HAS_SYMBOL_DEDUPE)
  endif()

  if(NOT DEFINED HAS_SYMBOL_DEDUPE)
    _test_weak_link_project(has_symbol_dedupe
                            HAS_SYMBOL_DEDUPE
                            SYMBOL_DEDUPE)

    set(HAS_SYMBOL_DEDUPE ${has_symbol_dedupe}
        CACHE BOOL "linker/loader can coalesce duplicated symbols")

    set(HAS_SYMBOL_DEDUPE_hash "${cmake_flags_hash}"
        CACHE INTERNAL "hashed flags for HAS_SYMBOL_DEDUPE check")
  endif()

  set(${resultVar} "${HAS_SYMBOL_DEDUPE}" PARENT_SCOPE)
endfunction()


function(target_link_libraries_with_dynamic_lookup target)
  has_dynamic_lookup(_dlookup)
  if(_dlookup)
    set_target_properties(${target}
                          PROPERTIES LINK_FLAGS "-undefined dynamic_lookup")
  else()
    has_symbol_dedupe(_dedupe)
    if(_dedupe)
      # loader coalesces duplicate symbols, so just link normally
      target_link_libraries(${target} ${ARGN})
    endif()
  endif()
endfunction()

