#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_skbuild
----------------------------------

Tests for `skbuild` module.
"""

import os
import platform
import sys

from skbuild.platform_specifics import get_platform

def test_generator_selection():
    version = sys.version_info
    env_generator = os.environ.get("CMAKE_GENERATOR")
    this_platform = platform.system().lower()
    get_best_generator = get_platform().get_best_generator
    arch = platform.architecture()

    if env_generator:
        assert(get_best_generator(env_generator) == env_generator)

    if this_platform == "windows":
        # assert that we are running a supported version of python
        py_27_32 = (
            (version.major == 2 and version.minor >= 7) or
            (version.major == 3 and version.minor <= 2)
        )

        py_33_34 = (
            version.major == 3 and (
                version.minor >= 3 and
                version.minor <= 4
            )
        )

        py_35 = (
            version.major == 3 and
            version.minor >= 5
        )

        assert(len(tuple(filter(bool, (py_27_32, py_33_34, py_35)))) == 1)

        generator = (
            "Visual Studio 9 2008" if py_27_32 else
            "Visual Studio 10 2010" if py_33_34 else
            "Visual Studio 14 2015"
        ) + (
            "Win64" if arch == "x64" else
            "ARM" if arch == "ARM" else
            ""
        )

        assert(get_best_generator() == generator)

