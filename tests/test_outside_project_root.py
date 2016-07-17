#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_outside_project_root
----------------------------------

Tries to build the `fail-outside-project-root` sample project.  Ensures that the
attempt fails with an SKBuildError exception.
"""

import os
import os.path
import shutil
import sys

from skbuild.exceptions import SKBuildError
from skbuild.cmaker import SKBUILD_DIR

def test_outside_project_root_installs():
    old_argv = sys.argv
    old_cwd = os.getcwd()

    sys.argv = ["setup.py", "install"]
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.join(cur_dir, "samples", "fail-outside-project-root"))

    if os.path.exists(SKBUILD_DIR):
        shutil.rmtree(SKBUILD_DIR)

    exception_thrown = False
    try:
        with open("setup.py", "r") as fp:
            exec(fp.read())
    except SKBuildError:
        exception_thrown = True
    finally:
        os.chdir(old_cwd)
        sys.argv = old_argv

    assert(exception_thrown)

