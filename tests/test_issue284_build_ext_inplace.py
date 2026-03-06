from __future__ import annotations

import platform
from pathlib import Path

import pytest

from . import get_ext_suffix


@pytest.mark.skipif(
    platform.python_implementation() == "PyPy", reason="PyPy is reporting an empty linker, doesn't seem to be our fault"
)
def test_build_ext_inplace_command(project_setup_py_test):
    with project_setup_py_test("issue-284-build-ext-inplace", ["build_ext", "--inplace"], disable_languages_test=True):
        assert Path(f"hello/_hello_sk{get_ext_suffix()}").exists()
        assert Path(f"hello/_hello_ext{get_ext_suffix()}").exists()
