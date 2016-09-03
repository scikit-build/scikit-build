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


def test_cmakelists_with_fatalerror_fails(capfd):

    with push_dir():

        @project_setup_py_test(("samples", "fail-with-fatal-error-cmakelists"),
                               ["build"],
                               clear_cache=True)
        def should_fail():
            pass

        failed = False
        try:
            should_fail()
        except SystemExit as e:
            failed = isinstance(e.code, SKBuildError)

    assert failed

    _, err = capfd.readouterr()
    assert "Invalid CMakeLists.txt" in err


def test_cmakelists_with_syntaxerror_fails(capfd):

    with push_dir():

        @project_setup_py_test(("samples", "fail-with-syntax-error-cmakelists"),
                               ["build"],
                               clear_cache=True)
        def should_fail():
            pass

        failed = False
        try:
            should_fail()
        except SystemExit as e:
            failed = isinstance(e.code, SKBuildError)

    assert failed

    _, err = capfd.readouterr()
    assert "Parse error.  Function missing ending \")\"" in err


def test_hello_with_compileerror_fails(capfd):

    with push_dir():

        @project_setup_py_test(("samples", "fail-hello-with-compile-error"),
                               ["build"],
                               clear_cache=True)
        def should_fail():
            pass

        failed = False
        try:
            should_fail()
        except SystemExit as e:
            failed = isinstance(e.code, SKBuildError)

    assert failed

    out, err = capfd.readouterr()
    assert "_hello.cxx" in out or "_hello.cxx" in err
