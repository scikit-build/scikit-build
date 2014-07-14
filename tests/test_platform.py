#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_platform
----------------------------------

Tests for platforms, to verify that CMake correctly does a test compilation.
"""

import os

from pycmake.platform_specifics import get_platform

# platform is shared across each test.  It's a platform-specific object that defines default CMake generator strings.
global platform
platform = get_platform()


def test_write_compiler_test_file():
    # write the file that CMake will use to test compile (empty list indicates we're testing no languages.)
    platform.write_test_cmakelist([])
    # verify that the test file exists (it's not valid, because it has no languages)
    assert(os.path.exists("cmake_test_compile/CMakeLists.txt"))


def test_cxx_compiler():
    platform.write_test_cmakelist(["CXX", "C"])
    # TODO: this isn't a true unit test.  It depends on the test CMakeLists.txt file having been written correctly.
    # with the known test file present, this tries to generate a makefile (or solution, or whatever).
    # This test verifies that a working compiler is present on the system, but doesn't actually compile anything.
    generator = platform.get_best_generator()
    assert(generator is not None)


def test_fortran_compiler():
    platform.write_test_cmakelist(["Fortran"])
    # TODO: this isn't a true unit test.  It depends on the test CMakeLists.txt file having been written correctly.
    # with the known test file present, this tries to generate a makefile (or solution, or whatever).
    # This test verifies that a working compiler is present on the system, but doesn't actually compile anything.
    generator = platform.get_best_generator()
    assert(generator is not None)


def test_generator_cleanup():
    # TODO: this isn't a true unit test.  It is assuming that the file was created at all, when it may not have been,
    #    and this test will be equally successful.
    platform.cleanup_test()
    assert(not os.path.exists("cmake_test_compile"))

