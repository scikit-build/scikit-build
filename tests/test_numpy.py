import os
import subprocess
import sys

import pytest

DIR = os.path.dirname(os.path.abspath(__file__))
HELLO_NUMPY = os.path.join(DIR, "samples/hello-numpy")
BASE = os.path.dirname(DIR)


@pytest.mark.skipif(sys.version_info < (3, 7), reason="Testing Python 3.")
def test_pep518(pep518):
    subprocess.check_call([sys.executable, "-m", "build", "--wheel"], cwd=HELLO_NUMPY)


@pytest.mark.skipif(sys.version_info < (3, 7), reason="Testing Python 3.")
def test_dual_pep518(pep518):
    subprocess.check_call([sys.executable, "-m", "build", "--wheel"], cwd=HELLO_NUMPY)
    subprocess.check_call([sys.executable, "-m", "build", "--wheel"], cwd=HELLO_NUMPY)
