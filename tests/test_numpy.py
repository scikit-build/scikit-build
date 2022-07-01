import os
import platform
import subprocess
import sys

import pytest

DIR = os.path.dirname(os.path.abspath(__file__))
HELLO_NUMPY = os.path.join(DIR, "samples/hello-numpy")
BASE = os.path.dirname(DIR)


@pytest.mark.skipif(
    platform.python_implementation() == "PyPy" and sys.version_info >= (3, 9),
    reason="NumPy not released for PyPy 3.9 yet",
)
def test_pep518_findpython(pep518):
    subprocess.check_call([sys.executable, "-m", "build", "--wheel"], cwd=HELLO_NUMPY)
