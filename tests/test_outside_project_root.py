#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_outside_project_root
----------------------------------

Tries to build the `fail-outside-project-root` sample project.  Ensures that the
attempt fails with a SystemExit exception that has an SKBuildError exception as
its value.
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

        failed = False
        try:
            should_fail()
        except SystemExit as e:
            failed = isinstance(e.code, SKBuildError)

        assert failed
