"""test_broken_project
----------------------------------

Tries to build the broken sample projects and ensures that each attempt fails
with a useful :class:`scikit_build_core.errors.FailedLiveProcessError`.
"""

from __future__ import annotations

import pytest
from scikit_build_core.errors import FailedLiveProcessError

from . import push_dir, push_env


def test_cmakelists_with_fatalerror_fails(capfd, project_setup_py_test):
    with push_dir(), push_env(CMAKE_GENERATOR=None):
        with pytest.raises(FailedLiveProcessError) as excinfo:
            with project_setup_py_test("fail-with-fatal-error-cmakelists", ["build"]):
                pass

    assert "CMake configuration failed" in str(excinfo.value)

    _, err = capfd.readouterr()
    assert "Invalid CMakeLists.txt" in err


def test_cmakelists_with_syntaxerror_fails(capfd, project_setup_py_test):
    with push_dir(), push_env(CMAKE_GENERATOR=None):
        with pytest.raises(FailedLiveProcessError) as excinfo:
            with project_setup_py_test("fail-with-syntax-error-cmakelists", ["build"]):
                pass

    assert "CMake configuration failed" in str(excinfo.value)

    _, err = capfd.readouterr()
    assert 'Parse error.  Function missing ending ")"' in err


def test_hello_with_compileerror_fails(capfd, project_setup_py_test):
    with push_dir(), push_env(CMAKE_GENERATOR=None):
        with pytest.raises(FailedLiveProcessError) as excinfo:
            with project_setup_py_test("fail-hello-with-compile-error", ["build"]):
                pass

    assert "CMake build failed" in str(excinfo.value)

    out, err = capfd.readouterr()
    assert "_hello.cxx" in out or "_hello.cxx" in err
