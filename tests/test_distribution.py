from __future__ import annotations

from pathlib import Path

from . import initialize_git_repo_and_commit, prepare_project

DIR = Path(__file__).parent.resolve()


def test_source_distribution(virtualenv, tmp_path):
    sdist_dir = tmp_path / "dist"
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    virtualenv.install("build")
    virtualenv.module("build", "--sdist", "--outdir", sdist_dir, cwd=DIR.parent)
    (sdist,) = sdist_dir.glob("*.tar.gz")

    virtualenv.install(sdist)

    prepare_project("hello-no-language", str(workspace), force=True)
    initialize_git_repo_and_commit(str(workspace), verbose=False)

    virtualenv.run("python", "setup.py", "bdist_wheel", cwd=workspace)


def test_wheel(virtualenv, tmp_path):
    wheel_dir = tmp_path / "dist"
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    virtualenv.install("build")
    virtualenv.module("build", "--wheel", "--outdir", wheel_dir, cwd=DIR.parent)
    (wheel,) = wheel_dir.glob("*.whl")

    virtualenv.install(wheel)

    prepare_project("hello-no-language", str(workspace), force=True)
    initialize_git_repo_and_commit(str(workspace), verbose=False)

    virtualenv.run("python", "setup.py", "bdist_wheel", cwd=workspace)
