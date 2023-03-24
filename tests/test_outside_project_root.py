"""test_outside_project_root
----------------------------------

Tries to build the `fail-outside-project-root` sample project.  Ensures that the
attempt fails with a SystemExit exception that has an SKBuildError exception as
its value.
"""

from __future__ import annotations

import pytest

from skbuild.exceptions import SKBuildError
from skbuild.utils import push_dir

from . import project_setup_py_test


@pytest.mark.parametrize("option", [None, "-DINSTALL_FILE:BOOL=1", "-DINSTALL_PROJECT:BOOL=1"])
def test_outside_project_root_fails(option):
    with push_dir():
        expected_failure = False

        cmd = ["install"]
        if option is not None:
            expected_failure = True
            cmd.extend(["--", option])

        @project_setup_py_test("fail-outside-project-root", cmd, disable_languages_test=True)
        def should_fail():
            pass

        failed = False
        msg = ""
        try:
            should_fail()
        except SystemExit as e:
            failed = isinstance(e.code, SKBuildError)
            msg = str(e)
        except SKBuildError as e:
            failed = True
            msg = str(e)

    assert expected_failure == failed

    if expected_failure:
        assert "CMake-installed files must be within the project root." in msg
