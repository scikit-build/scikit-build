import importlib.util
import os
import subprocess
import sys

import pytest

if sys.version_info < (3, 8):
    import importlib_metadata as metadata
else:
    from importlib import metadata


HAS_SETUPTOOLS_SCM = importlib.util.find_spec("setuptools_scm") is not None

DIR = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(DIR)


pytest.register_assert_rewrite("tests.pytest_helpers")


@pytest.fixture(scope="session")
def pep518_wheelhouse(tmpdir_factory):
    wheelhouse = tmpdir_factory.mktemp("wheelhouse")
    dist = tmpdir_factory.mktemp("dist")
    subprocess.run([sys.executable, "-m", "build", "--wheel", "--outdir", str(dist)], cwd=BASE, check=True)
    (wheel_path,) = dist.visit("*.whl")
    subprocess.run([sys.executable, "-m", "pip", "download", "-q", "-d", str(wheelhouse), str(wheel_path)], check=True)
    subprocess.run(
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
            "numpy",
        ],
        check=True,
    )
    return str(wheelhouse)


@pytest.fixture
def pep518(pep518_wheelhouse, monkeypatch):
    monkeypatch.setenv("PIP_FIND_LINKS", pep518_wheelhouse)
    monkeypatch.setenv("PIP_NO_INDEX", "true")
    return pep518_wheelhouse


def pytest_report_header() -> str:
    interesting_packages = {
        "build",
        "distro",
        "packaging",
        "pip",
        "setuptools",
        "setuptools_scm",
        "virtualenv",
        "wheel",
    }
    valid = []
    for package in interesting_packages:
        try:
            version = metadata.version(package)  # type: ignore[no-untyped-call]
        except ModuleNotFoundError:
            continue
        valid.append(f"{package}=={version}")
    reqs = " ".join(sorted(valid))
    pkg_line = f"installed packages of interest: {reqs}"

    return "\n".join([pkg_line])


def pytest_runtest_setup(item: pytest.Item) -> None:
    if HAS_SETUPTOOLS_SCM and tuple(item.iter_markers(name="nosetuptoolsscm")):
        pytest.exit("Setuptools_scm installed and nosetuptoolsscm tests not skipped.")
