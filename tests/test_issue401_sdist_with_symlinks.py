import glob
import sys
import tarfile

import py.path
import pytest

from . import (
    _tmpdir, execute_setup_py, prepare_project
)
from .pytest_helpers import check_sdist_content


@pytest.mark.skipif(sys.platform == 'win32', reason='Symlinks not supported on Windows')
def test_sdist_with_symlinks():
    project = 'issue-401-sdist-with-symlinks'

    tmp_dir = _tmpdir('test_sdist_with_symlinks')
    # NOTE: Existing prepare_project will remove symlinks, which renders the test useless
    prepare_project(project, tmp_dir)

    # Create a symbolic link
    # NOTE: We are creating the symlink after copying because prepare_project removes symlinks
    #       created in the samples directory.
    link_file = py.path.local(tmp_dir).join('VERSION')
    link_target = py.path.local(tmp_dir).join('VERSION.actual')
    link_file.mksymlinkto(link_target, absolute=False)

    expected_content = [
        'hello-1.2.3/README',
        'hello-1.2.3/setup.py',
        'hello-1.2.3/VERSION',
    ]

    with execute_setup_py(tmp_dir, ['sdist']):
        sdists_tar = glob.glob('dist/*.tar.gz')
        sdists_zip = glob.glob('dist/*.zip')
        assert sdists_tar or sdists_zip

        if sdists_tar:
            check_sdist_content(sdists_tar[0], 'hello-1.2.3', expected_content)

            with tarfile.open(sdists_tar[0], 'r:gz') as tf:
                member_list = tf.getnames()
                assert 'hello-1.2.3/VERSION' in member_list
                mbr = tf.getmember('hello-1.2.3/VERSION')
                assert not mbr.issym()
        elif sdists_zip:
            check_sdist_content(sdists_zip[0], 'hello-1.2.3', expected_content)
