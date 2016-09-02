#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_broken_cmakelists
----------------------------------

Tries to build the `fail-with-*-cmakelists` sample projects.  Ensures that the
attempt fails with a SystemExit exception that has an SKBuildError exception as
its value.
"""

from skbuild.exceptions import SKBuildError

from . import project_setup_py_test, push_dir


def test_cmakelists_with_fatalerror_fails():

    with push_dir():

        @project_setup_py_test(("samples", "fail-with-fatal-error-cmakelists"),
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


def test_cmakelists_with_syntaxerror_fails():

    with push_dir():

        @project_setup_py_test(("samples", "fail-with-syntax-error-cmakelists"),
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


def test_hello_with_compileerror_fails():

    with push_dir():

        @project_setup_py_test(("samples", "fail-hello-with-compile-error"),
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
