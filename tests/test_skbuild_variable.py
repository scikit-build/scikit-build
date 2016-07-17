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

    sys.argv = ["setup.py", "install"]
    os.chdir(os.path.join("samples", "fail-unless-skbuild-set"))

    if os.path.exists(SKBUILD_DIR):
        shutil.rmtree(SKBUILD_DIR)

    try:
        exec(open("setup.py").read())
    finally:
        os.chdir(old_cwd)
        sys.argv = old_argv

