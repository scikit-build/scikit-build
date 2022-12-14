#!/usr/bin/env python

"""test_skbuild
----------------------------------

Tests for `skbuild` module.
"""

import os
import platform
import sys
from shutil import which

import pytest

from skbuild.constants import CMAKE_BUILD_DIR
from skbuild.exceptions import SKBuildError
from skbuild.platform_specifics import get_platform
from skbuild.platform_specifics.windows import VS_YEAR_TO_VERSION, find_visual_studio

from . import get_cmakecache_variables, project_setup_py_test, push_dir, push_env


def test_generator_selection():
    env_generator = os.environ.get("CMAKE_GENERATOR")
    this_platform = platform.system().lower()
    get_best_generator = get_platform().get_best_generator
    arch = platform.architecture()[0]

    if env_generator:
        assert get_best_generator(env_generator).name == env_generator

    if this_platform == "windows":
        # Expected Visual Studio version
        vs_generator = "Visual Studio 15 2017"
        vs_version = 15

        vs_generator += " Win64" if arch == "64bit" else ""

        has_vs_2017 = find_visual_studio(vs_version=VS_YEAR_TO_VERSION["2017"])
        has_vs_2019 = find_visual_studio(vs_version=VS_YEAR_TO_VERSION["2019"])
        has_vs_2022 = find_visual_studio(vs_version=VS_YEAR_TO_VERSION["2022"])

        # As of Dec 2016, this is available only for VS 9.0
        has_vs_for_python_vcvars = any(
            [
                os.path.exists(os.path.expanduser(path_pattern % vs_version))
                for path_pattern in [
                    "~/AppData/Local/Programs/Common/Microsoft/Visual C++ for Python/%.1f/vcvarsall.bat",
                    "C:/Program Files (x86)/Common Files/Microsoft/Visual C++ for Python/%.1f/vcvarsall.bat",
                ]
            ]
        )

        # If environment exists, update the expected generator
        if has_vs_for_python_vcvars and which("ninja.exe"):
            assert get_best_generator().name == "Ninja"

        elif has_vs_2017:
            vs_generator = "Visual Studio 15 2017"
            # Early versions of 2017 may not ship with Ninja (TODO: check)
            assert get_best_generator().name in {"Ninja", vs_generator}

        elif has_vs_2019 or has_vs_2022:
            # ninja is provided by the CMake extension bundled with Visual Studio 2017
            # C:/Program Files (x86)/Microsoft Visual Studio/2017/Professional/Common7/IDE/CommonExtensions/Microsoft/CMake/Ninja/ninja.exe  # noqa: E501
            assert get_best_generator().name == "Ninja"

        elif has_vs_for_python_vcvars:
            assert get_best_generator().name == "NMake Makefiles"

    elif this_platform in ["darwin", "linux"]:
        generator = "Ninja" if which("ninja") else "Unix Makefiles"
        assert get_best_generator().name == generator


@pytest.mark.parametrize("generator, expected_make_program", [("NMake Makefiles", "nmake"), ("Unix Makefiles", "make")])
def test_generator(generator, expected_make_program):

    generator_platform = {"NMake Makefiles": ["windows"], "Unix Makefiles": ["darwin", "linux"]}
    assert generator in generator_platform

    this_platform = platform.system().lower()
    if this_platform not in generator_platform[generator]:
        pytest.skip(f"{generator} generator is not available on {this_platform.title()}")

    @project_setup_py_test("hello-cpp", ["build"], ret=True)
    def run_build():
        pass

    with push_env(CMAKE_GENERATOR=generator):
        tmp_dir = run_build()[0]
        cmakecache = tmp_dir.join(CMAKE_BUILD_DIR()).join("CMakeCache.txt")
        assert cmakecache.exists()
        variables = get_cmakecache_variables(str(cmakecache))
        make_program = variables["CMAKE_MAKE_PROGRAM"][1] if "CMAKE_MAKE_PROGRAM" in variables else ""
        assert make_program.endswith(expected_make_program) or make_program.endswith("%s.exe" % expected_make_program)


@pytest.mark.parametrize(
    "generator_args",
    [
        ["-G", "invalid"],
        ["--", "-G", "invalid"],
    ],
)
def test_invalid_generator(generator_args):
    with push_dir():

        build_args = ["build"]
        build_args.extend(generator_args)

        @project_setup_py_test("hello-no-language", build_args, disable_languages_test=True)
        def run():
            pass

        failed = False
        message = ""
        try:
            run()
        except SystemExit as e:
            failed = isinstance(e.code, SKBuildError)
            message = str(e)

        assert failed
        assert "scikit-build could not get a working generator " "for your system. Aborting build." in message


@pytest.mark.skipif(sys.platform != "win32", reason="Requires Windows")
@pytest.mark.parametrize("vs_year", ["2017", "2019", "2022"])
def test_platform_windows_find_visual_studio(vs_year, capsys):
    """If the environment variable ``SKBUILD_TEST_FIND_VS<vs_year>_INSTALLATION_EXPECTED`` is set,
    this test asserts the value returned by :func:`skbuild.platforms.windows.find_visual_studio()`.
    It skips the test otherwise.

    Setting the environment variable to 1 means that the corresponding Visual Studio version
    is expected to be installed. Setting it to 0, means otherwise.
    """
    env_var = "SKBUILD_TEST_FIND_VS%s_INSTALLATION_EXPECTED" % vs_year
    if env_var not in os.environ:
        pytest.skip("env. variable %s is not set" % env_var)

    valid_path_expected = bool(int(os.environ[env_var]))
    vs_path = find_visual_studio(VS_YEAR_TO_VERSION[vs_year])
    if valid_path_expected:
        with capsys.disabled():
            print(f"\nFound VS {vs_year} @ {vs_path}")
        assert os.path.exists(vs_path)
    else:
        assert vs_path == ""


@pytest.mark.skipif(sys.platform != "win32", reason="Requires Windows")
def test_toolset():
    has_vs_2017 = find_visual_studio(vs_version=VS_YEAR_TO_VERSION["2017"])
    if not has_vs_2017:
        pytest.skip("Visual Studio 15 2017 is not found")

    arch = platform.architecture()[0]
    vs_generator = "Visual Studio 15 2017"
    orig_generator = vs_generator
    if arch == "64bit":
        vs_generator += " Win64"

    @project_setup_py_test("hello-cpp", ["build", "-G", vs_generator], ret=True)
    def run_build():
        pass

    tmp_dir = run_build()[0]

    cmakecache = tmp_dir.join(CMAKE_BUILD_DIR()).join("CMakeCache.txt")
    variables = get_cmakecache_variables(str(cmakecache))

    generator = variables["CMAKE_GENERATOR"][1]
    assert generator == orig_generator

    var_toolset = variables["CMAKE_GENERATOR_TOOLSET"]
    toolset = var_toolset[1]

    assert toolset == "v141"
