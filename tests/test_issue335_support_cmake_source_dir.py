
from . import (
    _tmpdir, execute_setup_py, initialize_git_repo_and_commit, prepare_project
)


def test_bdist_wheel_command():
    project = "issue-335-support-cmake-source-dir"
    tmp_dir = _tmpdir('test_bdist_wheel_command')
    prepare_project(project, tmp_dir)
    initialize_git_repo_and_commit(tmp_dir, verbose=True)

    relative_setup_path = 'wrapping/python/'

    with execute_setup_py(tmp_dir.join(relative_setup_path), ["bdist_wheel"]):
        pass
