"""test_cmake_target
----------------------------------

Checks that the `test-cmake-target` sample project, which uses the
`cmake_install_target` keyword, now fails with a useful error message:
custom install targets are not supported by the scikit-build-core backend.
"""

from __future__ import annotations

import pytest


def test_cmake_install_target_errors(project_setup_py_test):
    with pytest.raises((SystemExit, AssertionError), match="cmake_install_target"):
        with project_setup_py_test("test-cmake-target", ["build"]):
            pass
