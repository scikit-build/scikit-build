#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_hello_cython
----------------------------------

Tries to build and test the `hello-cython-manifest` sample project.
"""

import glob

from . import get_ext_suffix, project_setup_py_test
from .pytest_helpers import check_sdist_content, check_wheel_content


@project_setup_py_test("hello-cython-manifest", ["build"])
def test_hello_cython_builds():
    pass


# @project_setup_py_test("hello-cython-manifest", ["test"])
# def test_hello_cython_works():
#     pass


@project_setup_py_test("hello-cython-manifest", ["sdist"])
def test_hello_cython_sdist():
    sdists_tar = glob.glob("dist/*.tar.gz")
    sdists_zip = glob.glob("dist/*.zip")
    assert sdists_tar or sdists_zip

    expected_content = [
        "hello-cython-manifest-1.2.3/CMakeLists.txt",
        "hello-cython-manifest-1.2.3/hello/_hello.pyx",
        "hello-cython-manifest-1.2.3/hello/CMakeLists.txt",
        "hello-cython-manifest-1.2.3/hello/__init__.py",
        "hello-cython-manifest-1.2.3/hello/__main__.py",
        "hello-cython-manifest-1.2.3/setup.py",
        "hello-cython-manifest-1.2.3/include-me.txt",
        "hello-cython-manifest-1.2.3/MANIFEST.in",
    ]

    sdist_archive = "dist/hello-cython-manifest-1.2.3.zip"
    if sdists_tar:
        sdist_archive = "dist/hello-cython-manifest-1.2.3.tar.gz"

    check_sdist_content(sdist_archive, "hello-cython-manifest-1.2.3", expected_content, package_dir="hello")


@project_setup_py_test("hello-cython-manifest", ["bdist_wheel"])
def test_hello_cython_wheel():
    expected_content = [
        "hello_cython_manifest-1.2.3.data/data/CMakeLists.txt",
        "hello_cython_manifest-1.2.3.data/data/MANIFEST.in",
        "hello_cython_manifest-1.2.3.data/data/include-me.txt",
        "hello_cython_manifest-1.2.3.data/data/setup.py",
        "hello_cython_manifest/CMakeLists.txt",
        "hello_cython_manifest/_hello.pyx",
        "hello_cython_manifest/_hello%s" % get_ext_suffix(),
        "hello_cython_manifest/__init__.py",
        "hello_cython_manifest/__main__.py",
    ]

    expected_distribution_name = "hello_cython_manifest-1.2.3"

    whls = glob.glob("dist/*.whl")
    assert len(whls) == 1
    check_wheel_content(whls[0], expected_distribution_name, expected_content)
