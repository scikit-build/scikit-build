
from . import (
    _tmpdir, execute_setup_py, initialize_git_repo_and_commit,
    prepare_project, push_dir
)


def test_test_command():
    tmp_dir = _tmpdir('test_test_command')
    project = "issue-335-support-cmake-source-dir"
    prepare_project(project, tmp_dir)
    initialize_git_repo_and_commit(tmp_dir, verbose=True)

    relative_setup_path = 'swig/python/'
    with push_dir(tmp_dir.join(relative_setup_path)):

        try:
            with execute_setup_py('.', ["bdist_wheel"], disable_languages_test=True):
                pass
        except SystemExit as exc:
            assert exc.code == 0
