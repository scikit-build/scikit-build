from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path

import pytest

DIR = Path(__file__).resolve().parent
HELLO_NUMPY = DIR / "samples/hello-numpy"
BASE = DIR.parent


@pytest.mark.isolated
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
