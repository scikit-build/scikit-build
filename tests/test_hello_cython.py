#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_hello_cython
----------------------------------

Tries to build and test the `hello-cython` sample project.
"""

import glob
import sysconfig
import tarfile

from zipfile import ZipFile

from . import project_setup_py_test


@project_setup_py_test("hello-cython", ["build"])
def test_hello_cython_builds():
    pass


# @project_setup_py_test("hello-cython", ["test"])
# def test_hello_cython_works():
#     pass


@project_setup_py_test("hello-cython", ["sdist"])
def test_hello_cython_sdist():
    sdists_tar = glob.glob('dist/*.tar.gz')
    sdists_zip = glob.glob('dist/*.zip')
    assert sdists_tar or sdists_zip

    expected_content = [
        'hello-cython-1.2.3/CMakeLists.txt',
        'hello-cython-1.2.3/hello/_hello.pyx',
        'hello-cython-1.2.3/hello/CMakeLists.txt',
        'hello-cython-1.2.3/hello/__init__.py',
        'hello-cython-1.2.3/hello/__main__.py',
        'hello-cython-1.2.3/setup.py',
        'hello-cython-1.2.3/PKG-INFO'
    ]

    member_list = None
    if sdists_tar:
        expected_content.extend([
            'hello-cython-1.2.3',
            'hello-cython-1.2.3/hello'
        ])
        member_list = tarfile.open('dist/hello-cython-1.2.3.tar.gz').getnames()

    elif sdists_zip:
        member_list = ZipFile('dist/hello-cython-1.2.3.zip').namelist()

    assert expected_content and member_list
    assert sorted(expected_content) == sorted(member_list)


@project_setup_py_test("hello-cython", ["bdist_wheel"])
def test_hello_cython_wheel():
    whls = glob.glob('dist/*.whl')
    assert len(whls) == 1
    assert not whls[0].endswith('-none-any.whl')

    expected_content = [
        'hello_cython-1.2.3.dist-info/top_level.txt',
        'hello_cython-1.2.3.dist-info/DESCRIPTION.rst',
        'hello_cython-1.2.3.dist-info/WHEEL',
        'hello_cython-1.2.3.dist-info/RECORD',
        'hello_cython-1.2.3.dist-info/metadata.json',
        'hello_cython-1.2.3.dist-info/METADATA',
        'hello_cython/_hello%s' % (sysconfig.get_config_var('SO')),
        'hello_cython/__init__.py',
        'hello_cython/__main__.py'
    ]

    member_list = ZipFile(whls[0]).namelist()
    assert sorted(expected_content) == sorted(member_list)
