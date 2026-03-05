from __future__ import annotations

import platform
from pathlib import Path

import pytest

from . import get_ext_suffix, project_setup_py_test


@pytest.mark.skipif(
    platform.python_implementation() == "PyPy", reason="PyPy is reporting an empty linker, doesn't seem to be our fault"
)
@project_setup_py_test("issue-284-build-ext-inplace", ["build_ext", "--inplace"], disable_languages_test=True)
def test_build_ext_inplace_command():
    assert Path(f"hello/_hello_sk{get_ext_suffix()}").exists()
    assert Path(f"hello/_hello_ext{get_ext_suffix()}").exists()
