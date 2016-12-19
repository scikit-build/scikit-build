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

        vs_ide_vcvars_path_pattern = \
            "C:/Program Files (x86)/" \
            "Microsoft Visual Studio %.1f/VC/vcvarsall.bat"

        # As of Dec 2016, this is available only for VS 9.0
        vs_for_python_vcvars_path_pattern = \
            "~/AppData/Local/Programs/Common/" \
            "Microsoft/Visual C++ for Python/%.1f/vcvarsall.bat"

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

        vs_ide_vcvars_path = vs_ide_vcvars_path_pattern % vs_version
        vs_for_python_vcvars_path = os.path.expanduser(
            vs_for_python_vcvars_path_pattern % vs_version)

        generator = None

        # If environment exists, update the expected generator
        if (
                    os.path.exists(vs_for_python_vcvars_path) or
                    os.path.exists(vs_ide_vcvars_path)
        ) and which("ninja.exe"):
            generator = "Ninja"

        elif os.path.exists(vs_ide_vcvars_path):
            generator = vs_generator

        elif os.path.exists(vs_for_python_vcvars_path):
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

    @project_setup_py_test("hello", ["build"])
    def run_build():
        pass

    with push_env(CMAKE_GENERATOR=generator):
        tmp_dir = run_build()[0]
        cmakecache = tmp_dir.join(CMAKE_BUILD_DIR).join("CMakeCache.txt")
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

        @project_setup_py_test("hello", build_args)
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
