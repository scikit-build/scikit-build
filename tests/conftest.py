import os
import subprocess
import sys

import pytest

DIR = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(DIR)


pytest.register_assert_rewrite("tests.pytest_helpers")


@pytest.fixture(scope="session")
def pep518_wheelhouse(tmpdir_factory):
    wheelhouse = tmpdir_factory.mktemp("wheelhouse")
    dist = tmpdir_factory.mktemp("dist")
    subprocess.check_call([sys.executable, "-m", "build", "--wheel", "--outdir", str(dist)], cwd=BASE)
    (wheel_path,) = dist.visit("*.whl")
    subprocess.check_call([sys.executable, "-m", "pip", "download", "-q", "-d", str(wheelhouse), str(wheel_path)])
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "download",
            "-q",
            "-d",
            str(wheelhouse),
            "build",
            "setuptools",
            "wheel",
            "ninja",
            "cmake",
        ]
    )
    return str(wheelhouse)


@pytest.fixture
def pep518(pep518_wheelhouse, monkeypatch):
    monkeypatch.setenv("PIP_FIND_LINKS", pep518_wheelhouse)
    monkeypatch.setenv("PIP_NO_INDEX", "true")
    return pep518_wheelhouse
