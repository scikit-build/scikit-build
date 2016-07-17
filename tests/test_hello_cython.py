#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_hello_cython
----------------------------------

Tries to build and test the `hello-cython` sample project.
"""

import os
import os.path
import shutil
import subprocess
import sys

from skbuild.exceptions import SKBuildError
from skbuild.cmaker import SKBUILD_DIR, CMAKE_BUILD_DIR

def test_hello_cython_builds():
    old_argv = sys.argv
    old_cwd = os.getcwd()

    sys.argv = ["setup.py", "build"]
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.join(cur_dir, "samples", "hello-cython"))

    if os.path.exists(SKBUILD_DIR):
        shutil.rmtree(SKBUILD_DIR)

    try:
        with open("setup.py", "r") as fp:
            exec(fp.read())
    finally:
        os.chdir(old_cwd)
        sys.argv = old_argv

def test_hello_cython_works():
    old_cwd = os.getcwd()
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.join(cur_dir, "samples", "hello-cython", CMAKE_BUILD_DIR))
    try:
        subprocess.check_call(
            ["ctest", "--build-config",
                os.environ.get("SKBUILD_CMAKE_CONFIG", "Debug"),
                "--output-on-failure"])
    finally:
        os.chdir(old_cwd)

