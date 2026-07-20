from __future__ import annotations

import pathlib
import platform
import sys
import textwrap

import pytest

from . import _tmpdir, cmake_build_dir, execute_setup_py, get_cmakecache_variables, push_env

pytestmark = pytest.mark.skipif(sys.platform != "darwin", reason="macOS-only behavior")


def _prepare_project(tmp_dir: pathlib.Path) -> None:
    """Write a tiny C project driven by ``skbuild.setup()`` into ``tmp_dir``."""

    (tmp_dir / "pyproject.toml").write_text("")
    (tmp_dir / "setup.py").write_text(
        textwrap.dedent(
            """
            from skbuild import setup
            setup(
                name="test_cmake_osx_args",
                version="1.2.3",
                description="A minimal example package",
                author="The scikit-build team",
                license="MIT",
            )
            """
        )
    )
    (tmp_dir / "hello.c").write_text("int hello(void) { return 42; }\n")
    (tmp_dir / "CMakeLists.txt").write_text(
        textwrap.dedent(
            """
            cmake_minimum_required(VERSION 3.15...3.26)
            project(hello C)
            add_library(hello STATIC hello.c)
            file(WRITE "${CMAKE_BINARY_DIR}/hello.txt" "hello")
            install(FILES "${CMAKE_BINARY_DIR}/hello.txt" DESTINATION ".")
            """
        )
    )


def _build_and_read_cmakecache(tmp_dir: pathlib.Path) -> dict[str, tuple[str, str]]:
    with execute_setup_py(tmp_dir, ["build"]):
        pass
    build_dir = cmake_build_dir(tmp_dir)
    assert build_dir is not None
    cmakecache = build_dir / "CMakeCache.txt"
    assert cmakecache.exists()
    variables: dict[str, tuple[str, str]] = get_cmakecache_variables(cmakecache)
    return variables


def test_osx_env_vars_set_cmake_osx_variables():
    """ARCHFLAGS and MACOSX_DEPLOYMENT_TARGET control CMAKE_OSX_ARCHITECTURES
    and CMAKE_OSX_DEPLOYMENT_TARGET (issue #342, scikit-build-core backend)."""

    tmp_dir = _tmpdir("cmake_osx_args_env_vars")
    _prepare_project(tmp_dir)

    arch = platform.machine()  # host-compatible so the build succeeds
    with push_env(ARCHFLAGS=f"-arch {arch}", MACOSX_DEPLOYMENT_TARGET="11.0", CMAKE_ARGS=None):
        variables = _build_and_read_cmakecache(tmp_dir)

    assert "CMAKE_OSX_ARCHITECTURES" in variables
    _, osx_architectures = variables["CMAKE_OSX_ARCHITECTURES"]
    assert osx_architectures == arch

    assert "CMAKE_OSX_DEPLOYMENT_TARGET" in variables
    _, osx_deployment_target = variables["CMAKE_OSX_DEPLOYMENT_TARGET"]
    assert osx_deployment_target == "11.0"


def test_osx_default_build():
    """Without env overrides, the build succeeds and the deployment target
    defaults to the one from the setuptools plat-name."""

    tmp_dir = _tmpdir("cmake_osx_args_default")
    _prepare_project(tmp_dir)

    with push_env(ARCHFLAGS=None, MACOSX_DEPLOYMENT_TARGET=None, CMAKE_ARGS=None):
        variables = _build_and_read_cmakecache(tmp_dir)

    # No ARCHFLAGS -> scikit-build-core does not pass CMAKE_OSX_ARCHITECTURES.
    assert variables.get("CMAKE_OSX_ARCHITECTURES", (None, ""))[1] == ""

    # The deployment target is always set in the CMake environment from the
    # setuptools plat-name, and CMake records it in the cache.
    assert "CMAKE_OSX_DEPLOYMENT_TARGET" in variables
    _, osx_deployment_target = variables["CMAKE_OSX_DEPLOYMENT_TARGET"]
    assert osx_deployment_target
