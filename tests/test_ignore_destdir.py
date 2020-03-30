import os
import os.path

from . import (
    _tmpdir, execute_setup_py, initialize_git_repo_and_commit, prepare_project
)


def test_ignore_DESTDIR_env_skbuild_install():
    project = 'hello-cpp'

    tmp_dir = _tmpdir('test_install_ignore_destdir')
    prepare_project(project, tmp_dir)
    initialize_git_repo_and_commit(tmp_dir, verbose=True)

    destdir = os.path.join(os.getcwd(), 'dest-dir')
    os.environ['DESTDIR'] = destdir
    with execute_setup_py(tmp_dir, ["build"]):
        assert not os.path.exists(destdir)


def test_ignore_MAKEFLAGS_DESTDIR_skbuild_install():
    project = 'hello-cpp'

    tmp_dir = _tmpdir('test_install_ignore_destdir')
    prepare_project(project, tmp_dir)
    initialize_git_repo_and_commit(tmp_dir, verbose=True)

    destdir = os.path.join(os.getcwd(), 'dest-dir')
    makeflags = 'CXXFLAGS=-Wall DESTDIR={}'.format(destdir)
    os.environ['MAKEFLAGS'] = makeflags
    with execute_setup_py(tmp_dir, ["build"]):
        assert not os.path.exists(destdir)
