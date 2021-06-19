#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_cmaker
----------------------------------

Tests for CMaker functionality.
"""

import os
import pytest
import re
import textwrap

from skbuild.cmaker import CMaker, has_cmake_cache_arg
from skbuild.constants import CMAKE_BUILD_DIR, CMAKE_DEFAULT_EXECUTABLE, CMAKE_INSTALL_DIR
from skbuild.exceptions import SKBuildError
from skbuild.utils import push_dir, to_unix_path

from . import _tmpdir, get_cmakecache_variables


def test_get_python_version():
    assert re.match(r'^[23](\.?)\d+$', CMaker.get_python_version())


def test_get_python_include_dir():
    python_include_dir = CMaker.get_python_include_dir(CMaker.get_python_version())
    assert python_include_dir
    assert os.path.exists(python_include_dir)


def test_get_python_library():
    python_library = CMaker.get_python_library(CMaker.get_python_version())
    assert python_library
    assert os.path.exists(python_library)


def test_cmake_executable():
    assert CMaker().cmake_executable == CMAKE_DEFAULT_EXECUTABLE


def test_has_cmake_cache_arg():
    cmake_args = ['-DFOO:STRING=42', '-DBAR', '-DCLIMBING:BOOL=ON']
    assert has_cmake_cache_arg(cmake_args, "FOO", "42")
    assert not has_cmake_cache_arg(cmake_args, "foo", "42")
    assert not has_cmake_cache_arg(cmake_args, "FOO", "43")
    assert not has_cmake_cache_arg(cmake_args, "BAR")
    assert not has_cmake_cache_arg(cmake_args, "BA")
    assert not has_cmake_cache_arg(cmake_args, "BAR", None)
    assert not has_cmake_cache_arg(cmake_args, "BAR", "42")
    assert has_cmake_cache_arg(cmake_args, "CLIMBING")
    assert has_cmake_cache_arg(cmake_args, "CLIMBING", None)
    assert has_cmake_cache_arg(cmake_args, "CLIMBING", "ON")

    override = ['-DOTHER:STRING=C', '-DOVERRIDE:STRING=A', '-DOVERRIDE:STRING=B']
    assert has_cmake_cache_arg(override, 'OVERRIDE')
    assert has_cmake_cache_arg(override, 'OVERRIDE', 'B')
    assert not has_cmake_cache_arg(override, 'OVERRIDE', 'A')
    # ensure overriding doesn't magically have side effects.
    assert has_cmake_cache_arg(override, 'OTHER')
    assert has_cmake_cache_arg(override, 'OTHER', 'C')
    assert not has_cmake_cache_arg(override, 'OTHER', 'A')
    assert not has_cmake_cache_arg(override, 'OTHER', 'B')


def test_make_without_build_dir_fails():
    src_dir = _tmpdir('test_make_without_build_dir_fails')
    with push_dir(str(src_dir)), pytest.raises(SKBuildError) as excinfo:
        CMaker().make()
    assert "Did you forget to run configure before make" in str(excinfo.value)


def test_make_without_configure_fails(capfd):
    src_dir = _tmpdir('test_make_without_configure_fails')
    src_dir.ensure(CMAKE_BUILD_DIR(), dir=1)
    with push_dir(str(src_dir)), pytest.raises(SKBuildError) as excinfo:
        CMaker().make()
    _, err = capfd.readouterr()
    assert "An error occurred while building with CMake." in str(excinfo.value)
    assert "Error: could not load cache" in err


@pytest.mark.parametrize("configure_with_cmake_source_dir", (True, False))
def test_make(configure_with_cmake_source_dir, capfd):
    tmp_dir = _tmpdir('test_make')
    with push_dir(str(tmp_dir)):

        src_dir = tmp_dir.ensure('SRC', dir=1)
        src_dir.join('CMakeLists.txt').write(textwrap.dedent(
            """
            cmake_minimum_required(VERSION 3.5.0)
            project(foobar NONE)
            file(WRITE "${CMAKE_BINARY_DIR}/foo.txt" "# foo")
            install(FILES "${CMAKE_BINARY_DIR}/foo.txt" DESTINATION ".")
            install(CODE "message(STATUS \\"Project has been installed\\")")
            message(STATUS "CMAKE_SOURCE_DIR:${CMAKE_SOURCE_DIR}")
            message(STATUS "CMAKE_BINARY_DIR:${CMAKE_BINARY_DIR}")
            """
        ))
        src_dir.ensure(CMAKE_BUILD_DIR(), dir=1)

        with push_dir(str(src_dir)
                      if not configure_with_cmake_source_dir
                      else str(tmp_dir.ensure('BUILD', dir=1))):
            cmkr = CMaker()
            config_kwargs = {}
            if configure_with_cmake_source_dir:
                config_kwargs['cmake_source_dir'] = str(src_dir)
            env = cmkr.configure(**config_kwargs)
            cmkr.make(env=env)

        messages = ["Project has been installed"]

        if configure_with_cmake_source_dir:
            messages += [
                "/SRC",
                "/BUILD/{}".format(to_unix_path(CMAKE_BUILD_DIR())),
                "/BUILD/{}/./foo.txt".format(to_unix_path(CMAKE_INSTALL_DIR()))
            ]
        else:
            messages += [
                "/SRC",
                "/SRC/{}".format(to_unix_path(CMAKE_BUILD_DIR())),
                "/SRC/{}/./foo.txt".format(to_unix_path(CMAKE_INSTALL_DIR())),
            ]

        out, _ = capfd.readouterr()
        for message in messages:
            assert message in out


def test_configure_with_cmake_args(capfd):
    tmp_dir = _tmpdir('test_configure_with_cmake_args')
    with push_dir(str(tmp_dir)):

        tmp_dir.join('CMakeLists.txt').write(textwrap.dedent(
            """
            cmake_minimum_required(VERSION 3.5.0)
            project(foobar NONE)
            # Do not complain about missing arguments passed to the main
            # project
            foreach(unused_var IN ITEMS
              ${CMAKE_EXPECTED_BAR}
              ${CMAKE_EXPECTED_FOO}
              ${PYTHON_EXECUTABLE}
              ${PYTHON_INCLUDE_DIR}
              ${PYTHON_LIBRARY}
              ${PYTHON_VERSION_STRING}
              ${SKBUILD}
              )
            endforeach()
            """
        ))

        with push_dir(str(tmp_dir)):
            cmkr = CMaker()
            cmkr.configure(clargs=[
                '-DCMAKE_EXPECTED_FOO:STRING=foo',
                '-DCMAKE_EXPECTED_BAR:STRING=bar'
            ], cleanup=False)

        cmakecache = tmp_dir.join(
            "_cmake_test_compile", "build", "CMakeCache.txt")
        assert cmakecache.exists()
        variables = get_cmakecache_variables(str(cmakecache))
        assert variables.get('CMAKE_EXPECTED_FOO', (None, None))[1] == "foo"
        assert variables.get('CMAKE_EXPECTED_BAR', (None, None))[1] == "bar"

        unexpected = "Manually-specified variables were not used by the project"
        _, err = capfd.readouterr()
        assert unexpected not in err


def test_check_for_bad_installs(tmpdir):
    with push_dir(str(tmpdir)):
        tmpdir.ensure(CMAKE_BUILD_DIR(), "cmake_install.cmake").write(textwrap.dedent(
            """
            file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/../hello" TYPE FILE FILES "/path/to/hello/world.py")
            """
        ))
        with pytest.raises(SKBuildError) as excinfo:
            CMaker.check_for_bad_installs()
        assert "CMake-installed files must be within the project root" in str(excinfo.value)
