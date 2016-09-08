#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_setup
----------------------------------

Tests for `skbuild.setup` function.
"""

import pytest

from distutils.core import Distribution as distutils_Distribution
from setuptools import Distribution as setuptool_Distribution

from skbuild import setup as skbuild_setup
from skbuild.utils import push_dir

from . import push_argv


@pytest.mark.parametrize("distribution_type",
                         ['unknown',
                          'py_modules',
                          'packages',
                          'skbuild'
                          ])
def test_distribution_is_pure(distribution_type, tmpdir):

    skbuild_setup_kwargs = {}

    if distribution_type == 'unknown':
        is_pure = False

    elif distribution_type == 'py_modules':
        is_pure = True
        hello_py = tmpdir.join("hello.py")
        hello_py.write("")
        skbuild_setup_kwargs["py_modules"] = ["hello"]

    elif distribution_type == 'packages':
        is_pure = True
        init_py = tmpdir.mkdir("hello").join("__init__.py")
        init_py.write("")
        skbuild_setup_kwargs["packages"] = ["hello"]

    elif distribution_type == 'skbuild':
        is_pure = False
        cmakelists_txt = tmpdir.join("CMakeLists.txt")
        cmakelists_txt.write(
            """
            cmake_minimum_required(VERSION 3.5.0)
            project(test NONE)
            install(CODE "execute_process(
              COMMAND \${CMAKE_COMMAND} -E sleep 0)")
            """
        )
    else:
        raise Exception(
            "Unknown distribution_type: {}".format(distribution_type))

    with push_dir(str(tmpdir)), push_argv(["setup.py", "build"]):
        distribution = skbuild_setup(
            name="test",
            version="0.0.1",
            description="test object returned by setup function",
            author="The scikit-build team",
            license="MIT",
            **skbuild_setup_kwargs
        )
        assert issubclass(distribution.__class__,
                          (distutils_Distribution, setuptool_Distribution))
        assert is_pure == distribution.is_pure()
