#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_hello_fortran
---------------------

Tries to build and test the `hello-fortran` sample project.
"""

import glob

from . import get_ext_suffix, project_setup_py_test
from .pytest_helpers import check_sdist_content, check_wheel_content


@project_setup_py_test("hello-fortran", ["build"])
def test_hello_fortran_build():
    pass


@project_setup_py_test("hello-fortran", ["sdist"])
def test_hello_fortran_sdist():
    sdists_tar = glob.glob('dist/*.tar.gz')
    sdists_zip = glob.glob('dist/*.zip')
    assert sdists_tar or sdists_zip

    expected_content = [
        'hello-fortran-1.2.3/bonjour/_bonjour.f90',
        'hello-fortran-1.2.3/bonjour/_bonjour.pyf',
        'hello-fortran-1.2.3/bonjour/CMakeLists.txt',
        'hello-fortran-1.2.3/CMakeLists.txt',
        'hello-fortran-1.2.3/hello/_hello.f90',
        'hello-fortran-1.2.3/hello/CMakeLists.txt',
        'hello-fortran-1.2.3/hello/__init__.py',
        'hello-fortran-1.2.3/hello/__main__.py',
        'hello-fortran-1.2.3/setup.py',
    ]

    sdist_archive = 'dist/hello-fortran-1.2.3.zip'
    if sdists_tar:
        sdist_archive = 'dist/hello-fortran-1.2.3.tar.gz'

    check_sdist_content(sdist_archive, 'hello-fortran-1.2.3', expected_content)


@project_setup_py_test("hello-fortran", ["bdist_wheel"])
def test_hello_fortran_wheel():
    expected_content = [
        'hello_fortran/_bonjour%s' % get_ext_suffix(),
        'hello_fortran/_hello%s' % get_ext_suffix(),
        'hello_fortran/__init__.py',
        'hello_fortran/__main__.py'
    ]

    expected_distribution_name = 'hello_fortran-1.2.3'

    whls = glob.glob('dist/*.whl')
    assert len(whls) == 1
    check_wheel_content(whls[0], expected_distribution_name, expected_content)
