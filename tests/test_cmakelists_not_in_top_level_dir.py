#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_cmakelists_not_in_top_level_dir
----------------------------------

Tries to build and test the `cmakelists_not_in_top_level_dir` sample
project. It basically checks that using the `cmake_source_dir` setup
keyword works.
"""

import glob
import pytest
import tarfile
import textwrap

from zipfile import ZipFile

from skbuild.exceptions import SKBuildError

from . import (_tmpdir, execute_setup_py, project_setup_py_test)


@project_setup_py_test("cmakelists-not-in-top-level-dir", ["build"])
def test_build(capsys):
    out, err = capsys.readouterr()
    dist_warning = "Unknown distribution option: 'cmake_source_dir'"
    assert (dist_warning not in err and dist_warning not in out)


@pytest.mark.parametrize("cmake_source_dir, expected_failed", (
        ("invalid", True),
        ("", False),
        (".", False),
))
def test_cmake_source_dir(cmake_source_dir, expected_failed):
    tmp_dir = _tmpdir('test_cmake_source_dir')

    tmp_dir.join('setup.py').write(textwrap.dedent(
        """
        from skbuild import setup
        setup(
            name="hello",
            version="1.2.3",
            description="a minimal example package",
            author='The scikit-build team',
            license="MIT",
            cmake_source_dir="{cmake_source_dir}"
        )
        """.format(cmake_source_dir=cmake_source_dir)
    ))
    failed = False
    message = ""
    try:
        with execute_setup_py(tmp_dir, ['build']):
            pass
    except SystemExit as e:
        failed = isinstance(e.code, SKBuildError)
        message = str(e)

    assert failed == expected_failed
    if failed:
        assert "'cmake_source_dir' set to a nonexistent directory." in message


@project_setup_py_test("cmakelists-not-in-top-level-dir", ["sdist"])
def test_hello_sdist():
    sdists_tar = glob.glob('dist/*.tar.gz')
    sdists_zip = glob.glob('dist/*.zip')
    assert sdists_tar or sdists_zip

    expected_content = [
        'hello-1.2.3/hello/_hello.cxx',
        'hello-1.2.3/hello/CMakeLists.txt',
        'hello-1.2.3/hello/__init__.py',
        'hello-1.2.3/hello/__main__.py',
        'hello-1.2.3/setup.py',
        'hello-1.2.3/PKG-INFO'
    ]

    member_list = None
    if sdists_tar:
        expected_content.extend([
            'hello-1.2.3',
            'hello-1.2.3/hello'
        ])
        member_list = tarfile.open('dist/hello-1.2.3.tar.gz').getnames()

    elif sdists_zip:
        member_list = ZipFile('dist/hello-1.2.3.zip').namelist()

    assert expected_content and member_list
    assert sorted(expected_content) == sorted(member_list)
