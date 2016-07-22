#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_outside_project_root
----------------------------------

Tries to build the `fail-outside-project-root` sample project.  Ensures that the
attempt fails with an SKBuildError exception.
"""

from skbuild.exceptions import SKBuildError

from . import project_setup_py_test


def test_outside_project_root_fails():
    @project_setup_py_test(("samples", "fail-outside-project-root"),
                           ["install"],
                           clear_cache=True)
    def should_fail():
        pass

    exception_thrown = False
    try:
        should_fail()
    except SKBuildError:
        exception_thrown = True

    assert exception_thrown
