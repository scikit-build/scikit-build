from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

DIR = Path(__file__).resolve().parent
HELLO_PEP518 = DIR / "samples/hello-pep518"
BASE = DIR.parent


@pytest.mark.isolated
@pytest.mark.skipif(sys.platform.startswith("cygwin"), reason="Needs release of scikit-build to make cmake work")
@pytest.mark.usefixtures("pep518")
def test_dual_pep518():
    # Building twice in a row must also work.
    subprocess.run([sys.executable, "-m", "build", "--wheel"], cwd=HELLO_PEP518, check=True)
    subprocess.run([sys.executable, "-m", "build", "--wheel"], cwd=HELLO_PEP518, check=True)
