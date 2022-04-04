#!/usr/bin/env python

"""test_cmake_target
----------------------------------

Tries to build and test the `test-cmake-target` sample
project. It basically checks that using the `cmake_target` keyword
in setup.py works.
"""

from . import project_setup_py_test


@project_setup_py_test("test-cmake-target", ["build"], disable_languages_test=True)
def test_cmake_target_build(capsys):
    out, err = capsys.readouterr()
    dist_warning = "Unknown distribution option: 'cmake_target'"
    assert dist_warning not in err and dist_warning not in out
