#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_manifest_in
----------------------------------

Tries to build and test the `manifest-in` sample project.
"""

import glob
import tarfile
import wheel

from pkg_resources import parse_version
from zipfile import ZipFile

from . import project_setup_py_test


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
    assert whls[0].endswith('-none-any.whl')

    expected_content = [
        'manifest_in-1.2.3.dist-info/top_level.txt',
        'manifest_in-1.2.3.dist-info/WHEEL',
        'manifest_in-1.2.3.dist-info/RECORD',
        'manifest_in-1.2.3.dist-info/METADATA',
        'hello/__init__.py'
    ]

    if parse_version(wheel.__version__) < parse_version('0.31.0'):
        expected_content += [
            'manifest_in-1.2.3.dist-info/DESCRIPTION.rst',
            'manifest_in-1.2.3.dist-info/metadata.json'
        ]

    member_list = ZipFile(whls[0]).namelist()
    assert sorted(expected_content) == sorted(member_list)
