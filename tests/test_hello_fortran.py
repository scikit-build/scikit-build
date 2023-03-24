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

    expected_content = [
        "hello-fortran-1.2.3/bonjour/_bonjour.f90",
        "hello-fortran-1.2.3/bonjour/_bonjour.pyf",
        "hello-fortran-1.2.3/bonjour/CMakeLists.txt",
        "hello-fortran-1.2.3/CMakeLists.txt",
        "hello-fortran-1.2.3/hello/_hello.f90",
        "hello-fortran-1.2.3/hello/CMakeLists.txt",
        "hello-fortran-1.2.3/hello/__init__.py",
        "hello-fortran-1.2.3/hello/__main__.py",
        "hello-fortran-1.2.3/setup.py",
    ]

    sdist_archive = "dist/hello-fortran-1.2.3.zip"
    if sdists_tar:
        sdist_archive = "dist/hello-fortran-1.2.3.tar.gz"

    check_sdist_content(sdist_archive, "hello-fortran-1.2.3", expected_content)


@pytest.mark.fortran()
@pytest.mark.skipif(sys.platform.startswith("win"), reason="Fortran not supported on Windows")
@pytest.mark.skipif(not ("FC" in os.environ or shutil.which("gfortran")), reason="GFortran required")
@project_setup_py_test("hello-fortran", ["bdist_wheel"])
def test_hello_fortran_wheel():
    expected_content = [
        "hello/_bonjour%s" % get_ext_suffix(),
        "hello/_hello%s" % get_ext_suffix(),
        "hello/__init__.py",
        "hello/__main__.py",
    ]

    expected_distribution_name = "hello_fortran-1.2.3"

    whls = glob.glob("dist/*.whl")
    assert len(whls) == 1
    check_wheel_content(whls[0], expected_distribution_name, expected_content)
