import os
import subprocess
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
HELLO_PEP518 = os.path.join(DIR, "samples/hello-pep518")
BASE = os.path.dirname(DIR)


def test_pep518(pep518):
    subprocess.check_call([sys.executable, "-m", "build", "--wheel"], cwd=HELLO_PEP518)


def test_dual_pep518(pep518):
    subprocess.check_call([sys.executable, "-m", "build", "--wheel"], cwd=HELLO_PEP518)
    subprocess.check_call([sys.executable, "-m", "build", "--wheel"], cwd=HELLO_PEP518)
