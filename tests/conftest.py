from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from collections.abc import Generator
from pathlib import Path

import pytest
import virtualenv as _virtualenv

if sys.version_info < (3, 8):
    import importlib_metadata as metadata
    from typing_extensions import Literal, overload
else:
    from importlib import metadata
    from typing import Literal, overload


HAS_SETUPTOOLS_SCM = importlib.util.find_spec("setuptools_scm") is not None

DIR = Path(__file__).parent.resolve()
BASE = DIR.parent


pytest.register_assert_rewrite("tests.pytest_helpers")


@pytest.fixture(scope="session")
def pep518_wheelhouse(tmp_path_factory) -> Path:
    numpy = ["numpy"] if sys.version_info < (3, 12) else []
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

    packages = [
        "build",
        "setuptools",
        "wheel",
        "ninja",
        "cmake",
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
    executable: Path
    env_dir: Path

    def __init__(self, env_dir: Path, *, wheelhouse: Path | None = None) -> None:
        cmd = [str(env_dir), "--no-setuptools", "--no-wheel", "--activators", ""]
        result = _virtualenv.cli_run(cmd, setup_logging=False)
        self.wheelhouse = wheelhouse
        self.executable = Path(result.creator.exe)
        self.env_dir = Path(result.creator.script_dir)

    @overload
    def run(self, *args: str | os.PathLike, capture: Literal[True], cwd: Path | None = ...) -> str:
        ...

    @overload
    def run(self, *args: str | os.PathLike, capture: Literal[False] = ..., cwd: Path | None = ...) -> None:
        ...

    def run(self, *args: str | os.PathLike, capture: bool = False, cwd: Path | None = None) -> str | None:
        __tracebackhide__ = True
        env = os.environ.copy()
        env["PATH"] = f"{self.executable.parent}{os.pathsep}{env['PATH']}"
        env["VIRTUAL_ENV"] = str(self.env_dir)
        env["PIP_DISABLE_PIP_VERSION_CHECK"] = "ON"
        if self.wheelhouse is not None:
            env["PIP_NO_INDEX"] = "ON"
            env["PIP_FIND_LINKS"] = str(self.wheelhouse)

        str_args = [os.fspath(a) for a in args]

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

    def execute(self, command: str, **kwargs: object) -> str:
        return self.run(str(self.executable), "-c", command, capture=True, **kwargs)

    def module(self, *args: str | os.PathLike, **kwargs: object) -> None:
        return self.run(str(self.executable), "-m", *args, **kwargs)

    def install(self, *args: str | os.PathLike) -> None:
        self.module("pip", "install", *args)


@pytest.fixture()
def pep518(pep518_wheelhouse, monkeypatch):
    monkeypatch.setenv("PIP_FIND_LINKS", str(pep518_wheelhouse))
    monkeypatch.setenv("PIP_NO_INDEX", "true")
    return pep518_wheelhouse


@pytest.fixture()
def isolated(tmp_path: Path, pep518_wheelhouse: Path) -> Generator[VEnv, None, None]:
    path = tmp_path / "venv"
    try:
        yield VEnv(path, wheelhouse=pep518_wheelhouse)
    finally:
        shutil.rmtree(path, ignore_errors=True)


@pytest.fixture()
def virtualenv(tmp_path: Path) -> Generator[VEnv, None, None]:
    path = tmp_path / "venv"
    try:
        yield VEnv(path)
    finally:
        shutil.rmtree(path, ignore_errors=True)


def pytest_report_header() -> str:
    interesting_packages = {
        "build",
        "distro",
        "packaging",
        "pip",
        "setuptools",
        "setuptools_scm",
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

    return "\n".join([pkg_line])


def pytest_runtest_setup(item: pytest.Item) -> None:
    if HAS_SETUPTOOLS_SCM and tuple(item.iter_markers(name="nosetuptoolsscm")):
        pytest.exit("Setuptools_scm installed and nosetuptoolsscm tests not skipped.")
