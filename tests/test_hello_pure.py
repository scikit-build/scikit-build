#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_hello_pure
----------------------------------

Tries to build and test the `hello-pure` sample project.
"""

import glob
import os
import tarfile
from zipfile import ZipFile

from skbuild.cmaker import SKBUILD_DIR
from skbuild.utils import push_dir

from . import project_setup_py_test


@project_setup_py_test(("samples", "hello-pure"), ["build"], clear_cache=True)
def test_hello_pure_builds(capsys):
    out, _ = capsys.readouterr()
    assert "skipping skbuild (no CMakeLists.txt found)" in out


# @project_setup_py_test(("samples", "hello-pure"), ["test"])
# def test_hello_cython_works():
#     pass


@project_setup_py_test(("samples", "hello-pure"), ["sdist"], clear_cache=True)
def test_hello_pure_sdist():
    sdists_tar = glob.glob('dist/*.tar.gz')
    sdists_zip = glob.glob('dist/*.zip')
    assert sdists_tar or sdists_zip

    member_list = None
    expected_content = None
    if sdists_tar:
        expected_content = [
            'hello-pure-1.2.3',
            'hello-pure-1.2.3/hello',
            'hello-pure-1.2.3/hello/__init__.py',
            'hello-pure-1.2.3/setup.py',
            'hello-pure-1.2.3/PKG-INFO'
        ]
        member_list = tarfile.open('dist/hello-pure-1.2.3.tar.gz').getnames()

    elif sdists_zip:
        expected_content = [
            'hello-pure-1.2.3/hello/__init__.py',
            'hello-pure-1.2.3/setup.py',
            'hello-pure-1.2.3/PKG-INFO'
        ]
        member_list = ZipFile('dist/hello-pure-1.2.3.zip').namelist()

    assert expected_content and member_list
    assert sorted(expected_content) == sorted(member_list)


@project_setup_py_test(("samples", "hello-pure"), ["bdist_wheel"])
def test_hello_pure_wheel():
    whls = glob.glob('dist/*.whl')
    assert len(whls) == 1
    assert whls[0].endswith('-none-any.whl')


def test_hello_clean(capfd):
    with push_dir():

        skbuild_dir = os.path.join(
            "tests", "samples", "hello-pure", SKBUILD_DIR)

        @project_setup_py_test(("samples", "hello-pure"), ["build"],
                               clear_cache=True)
        def run_build():
            pass

        run_build()

        assert os.path.exists(skbuild_dir)

        @project_setup_py_test(("samples", "hello-pure"), ["clean"])
        def run_clean():
            pass

        run_clean()

        assert not os.path.exists(skbuild_dir)

        out = capfd.readouterr()[0]
        assert 'Build files have been written to' not in out
