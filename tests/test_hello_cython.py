#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_hello_cython
----------------------------------

Tries to build and test the `hello-cython` sample project.
"""

import glob

from . import project_setup_py_test


@project_setup_py_test(("samples", "hello-cython"), ["build"], clear_cache=True)
def test_hello_cython_builds():
    pass


# @project_setup_py_test(("samples", "hello-cython"), ["test"])
# def test_hello_cython_works():
#     pass


@project_setup_py_test(("samples", "hello-cython"), ["sdist"])
def test_hello_cython_sdist():
    sdists_tar = glob.glob('dist/*.tar.gz')
    sdists_zip = glob.glob('dist/*.zip')
    assert sdists_tar or sdists_zip


@project_setup_py_test(("samples", "hello-cython"), ["bdist_wheel"])
def test_hello_cython_wheel():
    whls = glob.glob('dist/*.whl')
    assert len(whls) == 1
    assert not whls[0].endswith('-none-any.whl')
