"""test_outside_project_root
----------------------------------

Tries to build the `fail-outside-project-root` sample project.  Ensures that the
attempt fails with a useful error when CMake installs files outside the
staging area.
"""

from __future__ import annotations

import pytest

from . import push_dir, push_env


@pytest.mark.parametrize("option", [None, "-DINSTALL_FILE:BOOL=1", "-DINSTALL_PROJECT:BOOL=1"])
def test_outside_project_root_fails(option, project_setup_py_test):
    with push_dir(), push_env(CMAKE_ARGS=option):
        expected_failure = option is not None

        failed = False
        msg = ""
        try:
            with project_setup_py_test("fail-outside-project-root", ["build"]):
                pass
        except SystemExit as e:
            failed = True
            msg = str(e)

    assert expected_failure == failed

    if expected_failure:
        assert "CMake-installed files must stay within the setuptools build directory" in msg
