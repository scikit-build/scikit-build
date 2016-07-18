#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_skbuild_variable
------------------------

Tries to build the `fail-unless-skbuild-set` sample project.  The CMake variable
"SKBUILD" must be set in order for the build to succeed.
"""

import os
import os.path
import shutil
import sys

from skbuild.cmaker import SKBUILD_DIR

def test_fail_unless_skbuild_set_installs():
    old_argv = sys.argv
    old_cwd = os.getcwd()

    sys.argv = ["setup.py", "build"]
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.join(cur_dir, "samples", "fail-unless-skbuild-set"))

    if os.path.exists(SKBUILD_DIR):
        shutil.rmtree(SKBUILD_DIR)

    try:
        with open("setup.py", "r") as fp:
            exec(fp.read())
    finally:
        os.chdir(old_cwd)
        sys.argv = old_argv

