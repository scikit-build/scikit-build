#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_hello_cython
----------------------------------

Tries to build and test the `hello-cython` sample project.
"""

from . import project_setup_py_test


@project_setup_py_test(("samples", "hello-cython"), ["build"], clear_cache=True)
def test_hello_cython_builds():
    pass


# @project_setup_py_test(("samples", "hello-cython"), ["test"])
# def test_hello_cython_works():
#     pass


@project_setup_py_test(("samples", "hello-cython"), ["bdist_wheel"])
def test_hello_cython_wheel():
    pass
