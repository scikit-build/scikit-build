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
    platform.python_implementation() == "PyPy",
    reason="NumPy wheels not reliably available for PyPy",
)
@pytest.mark.usefixtures("pep518")
def test_pep518_findpython():
    subprocess.run([sys.executable, "-m", "build", "--wheel"], cwd=HELLO_NUMPY, check=True)
