#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob


"""test_hello
----------------------------------

Tries to build and test the `hello` sample project.
"""

from . import project_setup_py_test


@project_setup_py_test(("samples", "hello"), ["build"], clear_cache=True)
def test_hello_builds():
    pass


# @project_setup_py_test(("samples", "hello"), ["test"])
# def test_hello_works():
#     pass


@project_setup_py_test(("samples", "hello"), ["bdist_wheel"])
def test_hello_wheel():
    whls = glob.glob('dist/*.whl')
    assert len(whls) == 1
    assert not whls[0].endswith('-none-any.whl')
