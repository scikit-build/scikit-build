#!/usr/bin/env python

"""test_hello_cython
----------------------------------

Tries to build and test the `hello-cython` sample project.
"""

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


# @project_setup_py_test("hello-cython", ["test"])
# def test_hello_cython_works():
#     pass


@project_setup_py_test("hello-cython", ["sdist"])
def test_hello_cython_sdist():
    sdists_tar = glob.glob("dist/*.tar.gz")
    sdists_zip = glob.glob("dist/*.zip")
    assert sdists_tar or sdists_zip

    expected_content = [
        "hello-cython-1.2.3/CMakeLists.txt",
        "hello-cython-1.2.3/hello/_hello.pyx",
        "hello-cython-1.2.3/hello/CMakeLists.txt",
        "hello-cython-1.2.3/hello/__init__.py",
        "hello-cython-1.2.3/hello/__main__.py",
        "hello-cython-1.2.3/setup.py",
    ]

    sdist_archive = "dist/hello-cython-1.2.3.zip"
    if sdists_tar:
        sdist_archive = "dist/hello-cython-1.2.3.tar.gz"

    check_sdist_content(sdist_archive, "hello-cython-1.2.3", expected_content, package_dir="hello")


@project_setup_py_test("hello-cython", ["bdist_wheel"])
def test_hello_cython_wheel():
    expected_content = [
        "hello_cython/_hello%s" % get_ext_suffix(),
        "hello_cython/__init__.py",
        "hello_cython/__main__.py",
    ]

    expected_distribution_name = "hello_cython-1.2.3"

    whls = glob.glob("dist/*.whl")
    assert len(whls) == 1
    check_wheel_content(whls[0], expected_distribution_name, expected_content)
