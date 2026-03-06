from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from collections.abc import Callable, Generator
from contextlib import AbstractContextManager, contextmanager
from importlib import metadata
from pathlib import Path
from typing import Literal, overload

import pytest
import virtualenv as _virtualenv

from . import _tmpdir, execute_setup_py, initialize_git_repo_and_commit, prepare_project

HAS_SETUPTOOLS_SCM = importlib.util.find_spec("setuptools_scm") is not None

DIR = Path(__file__).parent.resolve()
BASE = DIR.parent


pytest.register_assert_rewrite("tests.pytest_helpers")


@pytest.fixture(scope="session")
def pep518_wheelhouse(tmp_path_factory: pytest.TempPathFactory) -> Path:
    numpy = ["numpy"] if sys.version_info < (3, 15) and sys.platform != "cygwin" else []
    wheelhouse = tmp_path_factory.mktemp("wheelhouse")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--wheel-dir",
            str(wheelhouse),
            f"{BASE}",
        ],
        check=True,
    )

    # Hatch-* packages only required for test_distribution
    packages = [
        "build",
        "setuptools",
        "virtualenv",
        "wheel",
        "ninja",
        "cmake",
        "hatch-fancy-pypi-readme",
        "hatch-vcs",
        "hatchling",
    ]

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "download",
            "-q",
            "-d",
            str(wheelhouse),
            *numpy,
            *packages,
        ],
        check=True,
    )
    return wheelhouse


class VEnv:
    def __init__(self, env_dir: Path, *, wheelhouse: Path | None = None) -> None:
        cmd = [str(env_dir), "--no-setuptools", "--no-wheel", "--activators", ""]
        result = _virtualenv.cli_run(cmd, setup_logging=False)
        self.wheelhouse = wheelhouse
        self.executable = Path(result.creator.exe)
        self.dest = env_dir.resolve()

    @overload
    def run(self, *args: str | os.PathLike[str], capture: Literal[True], cwd: Path | None = ...) -> str: ...

    @overload
    def run(self, *args: str | os.PathLike[str], capture: Literal[False] = ..., cwd: Path | None = ...) -> None: ...

    def run(self, *args: str | os.PathLike[str], capture: bool = False, cwd: Path | None = None) -> str | None:
        __tracebackhide__ = True
        env = os.environ.copy()
        env["PATH"] = f"{self.executable.parent}{os.pathsep}{env['PATH']}"
        env["VIRTUAL_ENV"] = str(self.dest)
        env["PIP_DISABLE_PIP_VERSION_CHECK"] = "ON"
        if self.wheelhouse is not None:
            env["PIP_NO_INDEX"] = "ON"
            env["PIP_FIND_LINKS"] = str(self.wheelhouse)

        str_args = [os.fspath(a) for a in args]

        # Windows does not make a python shortcut in venv
        if str_args[0] in {"python", "python3"}:
            str_args[0] = str(self.executable)

        if capture:
            result = subprocess.run(
                str_args,
                check=False,
                capture_output=True,
                text=True,
                env=env,
                cwd=cwd,
            )
            if result.returncode != 0:
                print(result.stdout, file=sys.stdout)
                print(result.stderr, file=sys.stderr)
                print("FAILED RUN:", *str_args, file=sys.stderr)
                raise SystemExit(result.returncode)
            return result.stdout.strip()

        result_bytes = subprocess.run(
            str_args,
            check=False,
            env=env,
            cwd=cwd,
        )
        if result_bytes.returncode != 0:
            print("FAILED RUN:", *str_args, file=sys.stderr)
            raise SystemExit(result_bytes.returncode)
        return None

    def execute(self, command: str, cwd: Path | None = None) -> str:
        return self.run(str(self.executable), "-c", command, capture=True, cwd=cwd)

    @overload
    def module(self, *args: str | os.PathLike[str], capture: Literal[False] = ..., cwd: Path | None = ...) -> None: ...

    @overload
    def module(self, *args: str | os.PathLike[str], capture: Literal[True], cwd: Path | None = ...) -> str: ...

    def module(self, *args: str | os.PathLike[str], capture: bool = False, cwd: Path | None = None) -> None | str:
        return self.run(str(self.executable), "-m", *args, capture=capture, cwd=cwd)  # type: ignore[no-any-return,call-overload]

    def install(self, *args: str | os.PathLike[str]) -> None:
        self.module("pip", "install", *args)


@pytest.fixture
def pep518(pep518_wheelhouse, monkeypatch):
    monkeypatch.setenv("PIP_FIND_LINKS", str(pep518_wheelhouse))
    monkeypatch.setenv("PIP_NO_INDEX", "true")
    return pep518_wheelhouse


@pytest.fixture
def isolated(tmp_path: Path, pep518_wheelhouse: Path) -> Generator[VEnv, None, None]:
    path = tmp_path / "venv"
    try:
        yield VEnv(path, wheelhouse=pep518_wheelhouse)
    finally:
        shutil.rmtree(path, ignore_errors=True)


@pytest.fixture
def project_setup_py_test() -> Callable[..., AbstractContextManager[Path]]:
    def _project_setup_py_test(
        project: str,
        setup_args: list[str],
        *,
        tmp_dir: Path | None = None,
        verbose_git: bool = True,
        disable_languages_test: bool = False,
    ) -> AbstractContextManager[Path]:
        project_dir = Path(tmp_dir) if tmp_dir is not None else _tmpdir(project)
        project_dir.mkdir(parents=True, exist_ok=True)
        prepare_project(project, project_dir)
        initialize_git_repo_and_commit(project_dir, verbose=verbose_git)

        @contextmanager
        def _runner() -> Generator[Path, None, None]:
            with execute_setup_py(project_dir, setup_args, disable_languages_test=disable_languages_test):
                yield project_dir

        return _runner()

    return _project_setup_py_test


def _get_program(name: str) -> str:
    res = shutil.which(name)
    if res is None:
        return f"No {name} executable found on PATH"
    result = subprocess.run([res, "--version"], check=True, text=True, capture_output=True)
    version = result.stdout.splitlines()[0]
    return f"{res}: {version}"


def pytest_report_header() -> str:
    interesting_packages = {
        "build",
        "cmake",
        "distro",
        "ninja",
        "packaging",
        "pip",
        "scikit-build",
        "setuptools",
        "setuptools_scm",
        "virtualenv",
        "wheel",
    }
    valid = []
    for package in interesting_packages:
        try:
            version = metadata.version(package)
        except ModuleNotFoundError:
            continue
        valid.append(f"{package}=={version}")
    reqs = " ".join(sorted(valid))
    pkg_line = f"installed packages of interest: {reqs}"
    prog_lines = [_get_program(n) for n in ("cmake3", "cmake", "ninja")]

    return "\n".join([pkg_line, *prog_lines])


def pytest_runtest_setup(item: pytest.Item) -> None:
    if HAS_SETUPTOOLS_SCM and tuple(item.iter_markers(name="nosetuptoolsscm")):
        pytest.exit("Setuptools_scm installed and nosetuptoolsscm tests not skipped.")
