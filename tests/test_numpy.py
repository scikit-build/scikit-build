import os
import subprocess
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
HELLO_NUMPY = os.path.join(DIR, "samples/hello-numpy")
BASE = os.path.dirname(DIR)


def test_pep518(pep518):
    subprocess.check_call([sys.executable, "-m", "build", "--wheel"], cwd=HELLO_NUMPY)


def test_dual_pep518(pep518):
    subprocess.check_call([sys.executable, "-m", "build", "--wheel"], cwd=HELLO_NUMPY)
    subprocess.check_call([sys.executable, "-m", "build", "--wheel"], cwd=HELLO_NUMPY)
