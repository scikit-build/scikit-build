from __future__ import annotations

import os
import subprocess
import sys

import pytest

DIR = os.path.dirname(os.path.abspath(__file__))
HELLO_PEP518 = os.path.join(DIR, "samples/hello-pep518")
BASE = os.path.dirname(DIR)


@pytest.mark.isolated()
@pytest.mark.skipif(sys.platform.startswith("cygwin"), reason="Needs release of scikit-build to make cmake work")
@pytest.mark.usefixtures("pep518")
def test_pep518():
    subprocess.run([sys.executable, "-m", "build", "--wheel"], cwd=HELLO_PEP518, check=True)


@pytest.mark.isolated()
@pytest.mark.skipif(sys.platform.startswith("cygwin"), reason="Needs release of scikit-build to make cmake work")
@pytest.mark.usefixtures("pep518")
def test_dual_pep518():
    subprocess.run([sys.executable, "-m", "build", "--wheel"], cwd=HELLO_PEP518, check=True)
    subprocess.run([sys.executable, "-m", "build", "--wheel"], cwd=HELLO_PEP518, check=True)
