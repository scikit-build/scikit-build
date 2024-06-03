"""test_hello_cython
----------------------------------

Tries to build and test the `hello-cython` sample project.
"""

from __future__ import annotations

import glob

import pytest

from . import get_ext_suffix, project_setup_py_test
from .pytest_helpers import check_sdist_content, check_wheel_content

pytestmark = pytest.mark.filterwarnings(
    "ignore:.*ends with a trailing slash, which is not supported by setuptools:FutureWarning"
)


@project_setup_py_test("hello-cython", ["build"])
def test_hello_cython_builds():
    pass


@project_setup_py_test("hello-cython", ["sdist"])
def test_hello_cython_sdist():
    sdists_tar = glob.glob("dist/*.tar.gz")
    sdists_zip = glob.glob("dist/*.zip")
    assert sdists_tar or sdists_zip

    dirname = "hello-cython-1.2.3"
    # setuptools 69.3.0 and above now canonicalize the filename as well.
    if any("hello_cython" in x for x in sdists_zip + sdists_tar):
        dirname = "hello_cython-1.2.3"

    expected_content = [
        f"{dirname}/CMakeLists.txt",
        f"{dirname}/hello/_hello.pyx",
        f"{dirname}/hello/CMakeLists.txt",
        f"{dirname}/hello/__init__.py",
        f"{dirname}/hello/__main__.py",
        f"{dirname}/setup.py",
    ]

    sdist_archive = f"dist/{dirname}.zip"
    if sdists_tar:
        sdist_archive = f"dist/{dirname}.tar.gz"

    check_sdist_content(sdist_archive, dirname, expected_content, package_dir="hello")


@project_setup_py_test("hello-cython", ["bdist_wheel"])
def test_hello_cython_wheel():
    expected_content = [
        f"hello_cython/_hello{get_ext_suffix()}",
        "hello_cython/__init__.py",
        "hello_cython/__main__.py",
    ]

    expected_distribution_name = "hello_cython-1.2.3"

    whls = glob.glob("dist/*.whl")
    assert len(whls) == 1
    check_wheel_content(whls[0], expected_distribution_name, expected_content)
