from __future__ import annotations

import os
import platform
import subprocess
import sys

import pytest

DIR = os.path.dirname(os.path.abspath(__file__))
HELLO_NUMPY = os.path.join(DIR, "samples/hello-numpy")
BASE = os.path.dirname(DIR)


@pytest.mark.isolated()
@pytest.mark.skipif(sys.platform.startswith("cygwin"), reason="Needs release of scikit-build to make cmake work")
@pytest.mark.skipif(
    platform.python_implementation() == "PyPy" and sys.version_info >= (3, 9),
    reason="NumPy not released for PyPy 3.9 yet",
)
@pytest.mark.skipif(
    sys.version_info >= (3, 12),
    reason="NumPy not released for Python 3.12 yet",
)
@pytest.mark.usefixtures("pep518")
def test_pep518_findpython():
    subprocess.run([sys.executable, "-m", "build", "--wheel"], cwd=HELLO_NUMPY, check=True)
