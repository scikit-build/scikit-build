from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

import nox

nox.needs_version = ">=2024.3.2"
nox.options.default_venv_backend = "uv|virtualenv"
nox.options.sessions = ["lint", "tests"]

PYTHON_ALL_VERSIONS = ["3.7", "3.8", "3.9", "3.10", "3.11", "3.12", "3.13", "pypy3.7", "pypy3.8", "pypy3.9", "pypy3.10"]
MSVC_ALL_VERSIONS = {"2017", "2019", "2022"}


@nox.session
def lint(session):
    """
    Run the linters.
    """
    session.install("pre-commit")
    session.run("pre-commit", "run", "-a")


@nox.session(python=PYTHON_ALL_VERSIONS)
def tests(session: nox.Session) -> None:
    """
    Run the tests.
    """
    posargs = list(session.posargs)
    env = os.environ.copy()

    # This should be handled via markers or some other pytest mechanism, but for now, this is usable.
    # nox -s tests-3.9 -- 2017 2019
    if sys.platform.startswith("win") and MSVC_ALL_VERSIONS & set(posargs):
        known_MSVC = {arg for arg in posargs if arg in MSVC_ALL_VERSIONS}
        posargs = [arg for arg in posargs if arg not in MSVC_ALL_VERSIONS]
        for version in MSVC_ALL_VERSIONS:
            contained = "1" if version in known_MSVC else "0"
            env[f"SKBUILD_TEST_FIND_VS{version}_INSTALLATION_EXPECTED"] = contained

    numpy = [] if "pypy" in session.python or "3.13" in session.python else ["numpy"]
    install_spec = "-e.[test,cov,doctest]" if "--cov" in posargs else ".[test,doctest]"
    if "--cov" in posargs:
        posargs.append("--cov-config=pyproject.toml")

    # Latest versions may break things, so grab them for testing!
    session.install("-U", "setuptools", "wheel", "virtualenv")
    session.install(install_spec, *numpy)
    session.run("pytest", *posargs, env=env)


@nox.session
def pylint(session):
    """
    Run PyLint.
    """

    session.install(".", "pylint", "cmake", "distro")
    session.run("pylint", "skbuild", *session.posargs)


@nox.session
def docs(session):
    """
    Build the docs. Use "-R" to rebuild faster. Check options with "-- -h".
    """

    parser = argparse.ArgumentParser(prog=f"{Path(sys.argv[0]).name} -s docs")
    parser.add_argument("--serve", action="store_true", help="Serve the docs")
    args = parser.parse_args(session.posargs)

    session.install("-e.[docs]")

    session.chdir("docs")
    shutil.rmtree("_build")
    session.run("sphinx-build", "-M", "html", ".", "_build", "-W")

    if args.serve:
        print("Launching docs at http://localhost:8000/ - use Ctrl-C to quit")
        session.run("python", "-m", "http.server", "8000", "-d", "_build/html")


@nox.session
def build(session):
    """
    Make an SDist and a wheel.
    """

    session.install("build")
    session.run("python", "-m", "build")


@nox.session(reuse_venv=True)
def build_api_docs(session: nox.Session) -> None:
    """
    Build (regenerate) API docs.
    """

    session.install("sphinx")
    session.chdir("docs")
    session.run(
        "sphinx-apidoc",
        "-o",
        ".",
        "--no-toc",
        "--force",
        "--module-first",
        "../skbuild",
    )


@nox.session(reuse_venv=True)
def downstream(session: nox.Session) -> None:
    """
    Build a downstream project.
    """

    # If running in manylinux:
    #   docker run --rm -v $PWD:/sk -w /sk -t quay.io/pypa/manylinux2014_x86_64:latest \
    #       pipx run --system-site-packages nox -s downstream -- https://github.com/...
    # (requires tomli, so allowing access to system-site-packages)

    parser = argparse.ArgumentParser(prog=f"{Path(sys.argv[0]).name} -s downstream")
    parser.add_argument("path", help="Location to git clone from")
    args, remaining = parser.parse_known_args(session.posargs)

    if sys.version_info < (3, 11):
        import tomli as tomllib
    else:
        import tomllib

    tmp_dir = Path(session.create_tmp())
    proj_dir = tmp_dir / "git"

    session.install("build", "hatch-fancy-pypi-readme", "hatch-vcs", "hatchling")
    session.install(".", "--no-build-isolation")

    if proj_dir.is_dir():
        session.chdir(proj_dir)
        session.run("git", "pull", external=True)
    else:
        session.run("git", "clone", args.path, *remaining, proj_dir, "--recurse-submodules", external=True)
        session.chdir(proj_dir)

    # Read and strip requirements
    pyproject_toml = Path("pyproject.toml")
    with pyproject_toml.open("rb") as f:
        pyproject = tomllib.load(f)
    requires = (x for x in pyproject["build-system"]["requires"] if "scikit-build" not in x.replace("_", "-"))
    session.install(*requires)

    session.run("python", "-m", "build", "--no-isolation", "--skip-dependency-check", "--wheel", ".")
