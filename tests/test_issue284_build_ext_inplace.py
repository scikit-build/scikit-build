import os
import sys

import pytest

from . import get_ext_suffix, project_setup_py_test

PYPY = hasattr(sys, "implementation") and sys.implementation.name == "pypy"


@pytest.mark.xfail(PYPY and sys.platform.startswith("darwin"), reason="Broken on PyPy on macOS")
@project_setup_py_test("issue-284-build-ext-inplace", ["build_ext", "--inplace"], disable_languages_test=True)
def test_build_ext_inplace_command():
    assert os.path.exists(f"hello/_hello_sk{get_ext_suffix()}")
    assert os.path.exists(f"hello/_hello_ext{get_ext_suffix()}")
