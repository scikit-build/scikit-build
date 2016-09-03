#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_broken_cmakelists
----------------------------------

Tries to build the `fail-with-*-cmakelists` sample projects.  Ensures that the
attempt fails with a SystemExit exception that has an SKBuildError exception as
its value.
"""

import pytest

from subprocess import CalledProcessError

from skbuild.exceptions import SKBuildError
from skbuild.utils import push_dir

from . import project_setup_py_test


def test_cmakelists_with_fatalerror_fails(capfd):

    with push_dir():

        @project_setup_py_test(("samples", "fail-with-fatal-error-cmakelists"),
                               ["build"],
                               clear_cache=True)
        def should_fail():
            pass

        failed = False
        message = ""
        try:
            should_fail()
        except SystemExit as e:
            failed = isinstance(e.code, SKBuildError)
            message = str(e)

    assert failed

    _, err = capfd.readouterr()
    assert "Invalid CMakeLists.txt" in err
    assert "An error occurred while configuring with CMake." in message


def test_cmakelists_with_syntaxerror_fails(capfd):

    with push_dir():

        @project_setup_py_test(("samples", "fail-with-syntax-error-cmakelists"),
                               ["build"],
                               clear_cache=True)
        def should_fail():
            pass

        failed = False
        message = ""
        try:
            should_fail()
        except SystemExit as e:
            failed = isinstance(e.code, SKBuildError)
            message = str(e)

    assert failed

    _, err = capfd.readouterr()
    assert "Parse error.  Function missing ending \")\"" in err
    assert "An error occurred while configuring with CMake." in message


def test_hello_with_compileerror_fails(capfd):

    with push_dir():

        @project_setup_py_test(("samples", "fail-hello-with-compile-error"),
                               ["build"],
                               clear_cache=True)
        def should_fail():
            pass

        failed = False
        message = ""
        try:
            should_fail()
        except SystemExit as e:
            failed = isinstance(e.code, SKBuildError)
            message = str(e)

    assert failed

    out, err = capfd.readouterr()
    assert "_hello.cxx" in out or "_hello.cxx" in err
    assert "An error occurred while building with CMake." in message


@pytest.mark.parametrize("exception", [CalledProcessError, OSError])
def test_invalid_cmake(exception, mocker):

    exceptions = {
        OSError: OSError('Unkown error'),
        CalledProcessError: CalledProcessError(['cmake', '--version'], 1)
    }

    mocker.patch('subprocess.check_call',
                 side_effect=exceptions[exception])

    with push_dir():

        @project_setup_py_test(("samples", "hello"), ["build"],
                               clear_cache=True)
        def should_fail():
            pass

        failed = False
        message = ""
        try:
            should_fail()
        except SystemExit as e:
            failed = isinstance(e.code, SKBuildError)
            message = str(e)

    assert failed
    assert "Problem with the CMake installation, aborting build." in message
