"""test_cython_flags
----------------------------------

Tries to build the `cython-flags` sample project.
"""

from __future__ import annotations


def test_hello_cython_builds(project_setup_py_test):
    with project_setup_py_test("cython-flags", ["build"]):
        pass
