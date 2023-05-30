from __future__ import annotations

from pathlib import Path

import pytest

from . import initialize_git_repo_and_commit, prepare_project

DIR = Path(__file__).parent.resolve()


@pytest.mark.isolated()
def test_source_distribution(isolated, tmp_path):
    sdist_dir = tmp_path / "dist"
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    isolated.install("build[virtualenv]")
    isolated.module("build", "--sdist", "--outdir", sdist_dir, cwd=DIR.parent)
    (sdist,) = sdist_dir.glob("*.tar.gz")

    isolated.install(sdist)

    prepare_project("hello-no-language", str(workspace), force=True)
    initialize_git_repo_and_commit(str(workspace), verbose=False)

    isolated.run("python", "setup.py", "bdist_wheel", cwd=workspace)


@pytest.mark.isolated()
def test_wheel(isolated, tmp_path):
    wheel_dir = tmp_path / "dist"
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    isolated.install("build[virtualenv]")
    isolated.module("build", "--wheel", "--outdir", wheel_dir, cwd=DIR.parent)
    (wheel,) = wheel_dir.glob("*.whl")

    isolated.install(wheel)

    prepare_project("hello-no-language", str(workspace), force=True)
    initialize_git_repo_and_commit(str(workspace), verbose=False)

    isolated.run("python", "setup.py", "bdist_wheel", cwd=workspace)
