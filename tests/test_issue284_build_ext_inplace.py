from __future__ import annotations

import os

from . import get_ext_suffix, project_setup_py_test


@project_setup_py_test("issue-284-build-ext-inplace", ["build_ext", "--inplace"], disable_languages_test=True)
def test_build_ext_inplace_command():
    assert os.path.exists(f"hello/_hello_sk{get_ext_suffix()}")
    assert os.path.exists(f"hello/_hello_ext{get_ext_suffix()}")
