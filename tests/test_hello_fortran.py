"""test_hello_fortran
---------------------

Tries to build and test the `hello-fortran` sample project.
"""

from __future__ import annotations

import glob
import os
import shutil
import sys

import pytest

from . import get_ext_suffix, project_setup_py_test
from .pytest_helpers import check_sdist_content, check_wheel_content

pytest.importorskip("numpy")


@pytest.mark.fortran()
@pytest.mark.skipif(sys.platform.startswith("win"), reason="Fortran not supported on Windows")
@pytest.mark.skipif(not ("FC" in os.environ or shutil.which("gfortran")), reason="GFortran required")
@project_setup_py_test("hello-fortran", ["build"])
def test_hello_fortran_build():
    pass


@pytest.mark.fortran()
@project_setup_py_test("hello-fortran", ["sdist"])
def test_hello_fortran_sdist():
    sdists_tar = glob.glob("dist/*.tar.gz")
    sdists_zip = glob.glob("dist/*.zip")
    assert sdists_tar or sdists_zip

    dirname = "hello-fortran-1.2.3"
    # setuptools 69.3.0 and above now canonicalize the filename as well.
    if any("hello_fortran" in x for x in sdists_zip + sdists_tar):
        dirname = "hello_fortran-1.2.3"

    expected_content = [
        f"{dirname}/bonjour/_bonjour.f90",
        f"{dirname}/bonjour/_bonjour.pyf",
        f"{dirname}/bonjour/CMakeLists.txt",
        f"{dirname}/CMakeLists.txt",
        f"{dirname}/hello/_hello.f90",
        f"{dirname}/hello/CMakeLists.txt",
        f"{dirname}/hello/__init__.py",
        f"{dirname}/hello/__main__.py",
        f"{dirname}/setup.py",
    ]

    sdist_archive = f"dist/{dirname}.zip"
    if sdists_tar:
        sdist_archive = f"dist/{dirname}.tar.gz"

    check_sdist_content(sdist_archive, dirname, expected_content)


@pytest.mark.fortran()
@pytest.mark.skipif(sys.platform.startswith("win"), reason="Fortran not supported on Windows")
@pytest.mark.skipif(not ("FC" in os.environ or shutil.which("gfortran")), reason="GFortran required")
@project_setup_py_test("hello-fortran", ["bdist_wheel"])
def test_hello_fortran_wheel():
    expected_content = [
        f"hello/_bonjour{get_ext_suffix()}",
        f"hello/_hello{get_ext_suffix()}",
        "hello/__init__.py",
        "hello/__main__.py",
    ]

    expected_distribution_name = "hello_fortran-1.2.3"

    whls = glob.glob("dist/*.whl")
    assert len(whls) == 1
    check_wheel_content(whls[0], expected_distribution_name, expected_content)
