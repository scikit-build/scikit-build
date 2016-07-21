#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_skbuild_variable
------------------------

Tries to build the `fail-unless-skbuild-set` sample project.  The CMake variable
"SKBUILD" must be set in order for the build to succeed.
"""

from . import project_setup_py_test


@project_setup_py_test(("samples", "fail-unless-skbuild-set"),
                       ["build"],
                       clear_cache=True)
def test_skbuild_variable_builds():
    pass


# @project_setup_py_test(("samples", "fail-unless-skbuild-set"), ["test"])
# def test_skbuild_variable_works():
#     pass


@project_setup_py_test(("samples", "fail-unless-skbuild-set"), ["bdist_wheel"])
def test_skbuild_variable_wheel():
    pass
