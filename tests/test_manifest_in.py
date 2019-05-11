#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_manifest_in
----------------------------------

Tries to build and test the `manifest-in` sample project.
"""

import glob
import tarfile

from zipfile import ZipFile

from . import project_setup_py_test
from .pytest_helpers import check_wheel_content


@project_setup_py_test("manifest-in", ["sdist"], disable_languages_test=True)
def test_manifest_in_sdist():
    sdists_tar = glob.glob('dist/*.tar.gz')
    sdists_zip = glob.glob('dist/*.zip')
    assert sdists_tar or sdists_zip

    member_list = None
    expected_content = None
    if sdists_tar:
        expected_content = [
            'manifest-in-1.2.3',
            'manifest-in-1.2.3/hello',
            'manifest-in-1.2.3/hello/__init__.py',
            'manifest-in-1.2.3/setup.py',
            'manifest-in-1.2.3/PKG-INFO'
        ]
        member_list = tarfile.open('dist/manifest-in-1.2.3.tar.gz').getnames()

    elif sdists_zip:
        expected_content = [
            'manifest-in-1.2.3/hello/__init__.py',
            'manifest-in-1.2.3/setup.py',
            'manifest-in-1.2.3/PKG-INFO'
        ]
        member_list = ZipFile('dist/manifest-in-1.2.3.zip').namelist()

    assert expected_content and member_list
    assert sorted(expected_content) == sorted(member_list)


@project_setup_py_test("manifest-in", ["bdist_wheel"], disable_languages_test=True)
def test_manifest_in_wheel():
    whls = glob.glob('dist/*.whl')
    assert len(whls) == 1

    expected_content = [
        'hello/__init__.py'
    ]

    expected_distribution_name = 'manifest_in-1.2.3'

    check_wheel_content(whls[0], expected_distribution_name, expected_content, pure=True)
