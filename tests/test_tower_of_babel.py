#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_tower_of_babel
----------------------------------

Tries to build and test the `tower-of-babel` sample project.
"""

import os
import os.path
import shutil
import subprocess
import sys

from skbuild.exceptions import SKBuildError
from skbuild.cmaker import SKBUILD_DIR, CMAKE_BUILD_DIR

def test_tbabel_builds():
    old_argv = sys.argv
    old_cwd = os.getcwd()

    sys.argv = ["setup.py", "build"]
    os.chdir(os.path.join("samples", "tower-of-babel"))

    if os.path.exists(SKBUILD_DIR):
        shutil.rmtree(SKBUILD_DIR)

    try:
        exec(open("setup.py").read())
    finally:
        os.chdir(old_cwd)
        sys.argv = old_argv

def test_tbabel_works():
    old_cwd = os.getcwd()
    os.chdir(os.path.join("samples", "tower-of-babel", CMAKE_BUILD_DIR))

    env = os.environ
    pp = env.get("PYTHONPATH", [])
    if(pp):
        pp = pp.split(os.pathsep)

    pyversion = "python" + ".".join(str(x) for x in sys.version_info[:2])
    pp.extend((
        os.path.join(sys.prefix, "lib", pyversion),
        os.path.join(sys.prefix, "lib", pyversion, "site-packages"),
        os.path.join(sys.prefix, "lib", pyversion, "lib-dynload"),
        os.getcwd()
    ))

    env["PYTHONPATH"] = os.pathsep.join(pp)

    env["PYTHONHOME"] = env.get("PYTHONHOME", sys.prefix)

    try:
        subprocess.check_call(
            ["ctest", "--build-config",
                os.environ.get("SKBUILD_CMAKE_CONFIG", "Debug"),
                "--output-on-failure"],
            env=env)
    finally:
        os.chdir(old_cwd)

