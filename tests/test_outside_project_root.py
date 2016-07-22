#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_outside_project_root
----------------------------------

Tries to build the `fail-outside-project-root` sample project.  Ensures that the
attempt fails with an SKBuildError exception.
"""

from skbuild.exceptions import SKBuildError

from . import project_setup_py_test, push_dir


def test_outside_project_root_fails():

    with push_dir():

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
