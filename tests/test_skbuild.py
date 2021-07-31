#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_skbuild
----------------------------------

Tests for `skbuild` module.
"""

import os
import platform
import pytest
import sys

from skbuild.constants import CMAKE_BUILD_DIR
from skbuild.exceptions import SKBuildError
from skbuild.platform_specifics import get_platform
from skbuild.platform_specifics.windows import find_visual_studio, VS_YEAR_TO_VERSION

from . import (get_cmakecache_variables, project_setup_py_test,
               push_dir, push_env, which)


def test_generator_selection():
    version = sys.version_info
    env_generator = os.environ.get("CMAKE_GENERATOR")
    this_platform = platform.system().lower()
    get_best_generator = get_platform().get_best_generator
    arch = platform.architecture()[0]

    if env_generator:
        assert(get_best_generator(env_generator).name == env_generator)

    if this_platform == "windows":
        # assert that we are running a supported version of python
        py_27_32 = (
            (version.major == 2 and version.minor >= 7) or
            (version.major == 3 and version.minor <= 2)
        )

        py_33_34 = (
            version.major == 3 and (
                3 <= version.minor <= 4
            )
        )

        py_35 = (
            version.major == 3 and
            version.minor >= 5
        )

        assert(len(tuple(filter(bool, (py_27_32, py_33_34, py_35)))) == 1)

        # Expected Visual Studio version
        if py_27_32:
            vs_generator = "Visual Studio 9 2008"
            vs_version = 9
        elif py_33_34:
            vs_generator = "Visual Studio 10 2010"
            vs_version = 10
        else:
            vs_generator = "Visual Studio 14 2015"
            vs_version = 14
        vs_generator += (" Win64" if arch == "64bit" else "")

        has_vs_2017 = find_visual_studio(vs_version=VS_YEAR_TO_VERSION["2017"])
        has_vs_2019 = find_visual_studio(vs_version=VS_YEAR_TO_VERSION["2019"])

        # Apply to VS <= 14 (2015)
        has_vs_ide_vcvars = any([
            os.path.exists(path_pattern % vs_version)
            for path_pattern in [
                "C:/Program Files (x86)/Microsoft Visual Studio %.1f/VC/vcvarsall.bat"
            ]
        ])

        # As of Dec 2016, this is available only for VS 9.0
        has_vs_for_python_vcvars = any([
            os.path.exists(os.path.expanduser(path_pattern % vs_version))
            for path_pattern in [
                "~/AppData/Local/Programs/Common/Microsoft/Visual C++ for Python/%.1f/vcvarsall.bat",
                "C:/Program Files (x86)/Common Files/Microsoft/Visual C++ for Python/%.1f/vcvarsall.bat"

            ]
        ])

        generator = None

        # If environment exists, update the expected generator
        if (
                has_vs_for_python_vcvars or has_vs_ide_vcvars
        ) and which("ninja.exe"):
            generator = "Ninja"

        elif has_vs_2017 or has_vs_2019:
            # ninja is provided by the CMake extension bundled with Visual Studio 2017
            # C:/Program Files (x86)/Microsoft Visual Studio/2017/Professional/Common7/IDE/CommonExtensions/Microsoft/CMake/Ninja/ninja.exe  # noqa: E501
            generator = "Ninja"

        elif has_vs_ide_vcvars or has_vs_2017:
            generator = vs_generator

        elif has_vs_for_python_vcvars:
            generator = "NMake Makefiles"

        assert (get_best_generator().name == generator)

    elif this_platform in ["darwin", "linux"]:
        generator = "Unix Makefiles"
        if which("ninja"):
            generator = "Ninja"
        assert get_best_generator().name == generator


@pytest.mark.parametrize("generator, expected_make_program", [
    ("NMake Makefiles", "nmake"),
    ("Unix Makefiles", "make")
])
def test_generator(generator, expected_make_program):

    generator_platform = {
        "NMake Makefiles": ["windows"],
        "Unix Makefiles": ["darwin", "linux"]
    }
    assert generator in generator_platform

    this_platform = platform.system().lower()
    if this_platform not in generator_platform[generator]:
        pytest.skip("%s generator is available only on %s" % (
            generator, this_platform.title()))

    @project_setup_py_test("hello-cpp", ["build"])
    def run_build():
        pass

    with push_env(CMAKE_GENERATOR=generator):
        tmp_dir = run_build()[0]
        cmakecache = tmp_dir.join(CMAKE_BUILD_DIR()).join("CMakeCache.txt")
        assert cmakecache.exists()
        variables = get_cmakecache_variables(str(cmakecache))
        make_program = (variables["CMAKE_MAKE_PROGRAM"][1]
                        if "CMAKE_MAKE_PROGRAM" in variables else "")
        assert make_program.endswith(expected_make_program) or \
            make_program.endswith("%s.exe" % expected_make_program)


@pytest.mark.parametrize(
    "generator_args",
    [
        ["-G", "invalid"],
        ["--", "-G", "invalid"],
    ]
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
        assert "scikit-build could not get a working generator " \
               "for your system. Aborting build." in message


@pytest.mark.parametrize(
    "vs_year", ["2008", "2010", "2012", "2013", "2015", "2017", "2019"]
)
def test_platform_windows_find_visual_studio(vs_year):
    """If the environment variable ``SKBUILD_TEST_FIND_VS<vs_year>_INSTALLATION_EXPECTED`` is set,
    this test asserts the value returned by :func:`skbuild.platforms.windows.find_visual_studio()`.
    It skips the test otherwise.

    Setting the environment variable to 1 means that the corresponding Visual Studio version
    is expected to be installed. Setting it to 0, means otherwise.
    """
    env_var = 'SKBUILD_TEST_FIND_VS%s_INSTALLATION_EXPECTED' % vs_year
    if env_var not in os.environ:
        pytest.skip("env. variable %s is not set" % env_var)

    valid_path_expected = bool(int(os.environ[env_var]))
    if valid_path_expected:
        assert os.path.exists(find_visual_studio(VS_YEAR_TO_VERSION[vs_year]))
    else:
        assert find_visual_studio(VS_YEAR_TO_VERSION[vs_year]) == ""


@pytest.mark.skipif(sys.version_info < (3, 5), reason="Python 3.5+ required on Windows")
@pytest.mark.skipif(sys.platform != 'win32', reason='Requires Windows')
def test_toolset():
    py_35 = sys.version_info[:2] == (3, 5)

    has_vs_2017 = find_visual_studio(vs_version=VS_YEAR_TO_VERSION["2017"])
    if not has_vs_2017:
        pytest.skip("Visual Studio 15 2017 is not found")

    arch = platform.architecture()[0]
    vs_generator = "Visual Studio 15 2017"
    orig_generator = vs_generator
    if arch == "64bit":
        vs_generator += " Win64"

    @project_setup_py_test("hello-cpp", ["build", "-G", vs_generator])
    def run_build():
        pass

    tmp_dir = run_build()[0]

    cmakecache = tmp_dir.join(CMAKE_BUILD_DIR()).join("CMakeCache.txt")
    variables = get_cmakecache_variables(str(cmakecache))

    generator = variables['CMAKE_GENERATOR'][1]
    assert generator == orig_generator

    var_toolset = variables['CMAKE_GENERATOR_TOOLSET']
    toolset = var_toolset[1]

    if py_35:
        assert toolset == "v140"
    else:
        assert toolset == "v141"
