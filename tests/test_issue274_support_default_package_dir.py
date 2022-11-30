import pytest

from . import (
    _tmpdir,
    execute_setup_py,
    initialize_git_repo_and_commit,
    prepare_project,
    project_setup_py_test,
    push_dir,
)


@pytest.mark.deprecated
@project_setup_py_test("issue-274-support-default-package-dir", ["install"], disable_languages_test=True)
def test_install_command():
    pass


@pytest.mark.deprecated
def test_test_command():
    with push_dir():

        tmp_dir = _tmpdir("test_test_command")
        project = "issue-274-support-default-package-dir"
        prepare_project(project, tmp_dir)
        initialize_git_repo_and_commit(tmp_dir, verbose=True)

        try:
            with execute_setup_py(tmp_dir, ["test"], disable_languages_test=True):
                pass
        except SystemExit as exc:
            assert exc.code == 0

        assert tmp_dir.join("test_hello.completed.txt").exists()
