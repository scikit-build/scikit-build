#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_setup
----------------------------------

Tests for `skbuild.setup` function.
"""

import textwrap
import pytest

from distutils.core import Distribution as distutils_Distribution
from setuptools import Distribution as setuptool_Distribution

from skbuild import setup as skbuild_setup
from skbuild.utils import push_dir

from . import (_tmpdir, execute_setup_py, push_argv)


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


@pytest.mark.parametrize("cmake_args", [
    [],
    ['--', '-DVAR:STRING=43', '-DVAR_WITH_SPACE:STRING=Ciao Mondo']
])
def test_cmake_args_keyword(cmake_args, capfd):
    tmp_dir = _tmpdir('cmake_args_keyword')

    tmp_dir.join('setup.py').write(textwrap.dedent(
        """
        from skbuild import setup
        setup(
            name="hello",
            version="1.2.3",
            description="a minimal example package",
            author='The scikit-build team',
            license="MIT",
            cmake_args=[
                "-DVAR:STRING=42",
                "-DVAR_WITH_SPACE:STRING=Hello World"
            ]

        )
        """
    ))
    tmp_dir.join('CMakeLists.txt').write(textwrap.dedent(
        """
        cmake_minimum_required(VERSION 3.5.0)
        project(test NONE)
        message(STATUS "VAR[${VAR}]")
        message(STATUS "VAR_WITH_SPACE[${VAR_WITH_SPACE}]")
        install(CODE "execute_process(
          COMMAND \${CMAKE_COMMAND} -E sleep 0)")
        """
    ))

    with execute_setup_py(tmp_dir, ['build'] + cmake_args):
        pass

    out, _ = capfd.readouterr()

    if not cmake_args:
        assert "VAR[42]" in out
        assert "VAR_WITH_SPACE[Hello World]" in out
    else:
        assert "VAR[43]" in out
        assert "VAR_WITH_SPACE[Ciao Mondo]" in out
