from __future__ import annotations

import glob

from . import _tmpdir, execute_setup_py, initialize_git_repo_and_commit, prepare_project
from .pytest_helpers import check_wheel_content


def test_bdist_wheel_command():
    project = "test-filter-manifest"

    expected_content = [
        "hello/__init__.py",
        "hello/swig_mwe.py",
        "hello/_swig_mwe.pyd",
        "hello-1.2.3.data/data/bin/hello",
    ]

    expected_distribution_name = "hello-1.2.3"

    tmp_dir = _tmpdir("test_bdist_wheel_command")
    prepare_project(project, tmp_dir)
    initialize_git_repo_and_commit(tmp_dir, verbose=True)

    relative_setup_path = "wrapping/python/"

    with execute_setup_py(tmp_dir.join(relative_setup_path), ["bdist_wheel"]):
        whls = glob.glob("dist/*.whl")
        assert len(whls) == 1
        check_wheel_content(whls[0], expected_distribution_name, expected_content)
