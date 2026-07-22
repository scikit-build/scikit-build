from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

import nox

nox.needs_version = ">=2025.02.09"
nox.options.default_venv_backend = "uv|virtualenv"

PYPROJECT = nox.project.load_toml("pyproject.toml")
PYTHON_VERSIONS = nox.project.python_versions(PYPROJECT)

PYTHON_ALL_VERSIONS = [*PYTHON_VERSIONS, "pypy3.8", "pypy3.9", "pypy3.10", "pypy3.11"]

SKBUILD_CORE_REQ = os.environ.get("SKBUILD_CORE_REQ", "scikit-build-core[setuptools]>=1.0")


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
    env["SKBUILD_CORE_REQ"] = SKBUILD_CORE_REQ

    numpy = [] if "pypy" in session.python or sys.platform == "cygwin" else ["numpy"]
    install_spec = "-e.[test,cov,doctest]" if "--cov" in posargs else ".[test,doctest]"
    if "--cov" in posargs:
        posargs.append("--cov-config=pyproject.toml")

    # Latest versions may break things, so grab them for testing!
    session.install("-U", "setuptools", "wheel", "virtualenv")
    session.install(SKBUILD_CORE_REQ)
    session.install(install_spec, *numpy)
    session.run("pytest", *posargs, env=env)


@nox.session(default=False)
def pylint(session):
    """
    Run PyLint.
    """

    session.install(SKBUILD_CORE_REQ)
    session.install(".", "pylint", "cmake")
    session.run("pylint", "skbuild", *session.posargs)


@nox.session(default=False)
def docs(session):
    """
    Build the docs. Use "-R" to rebuild faster. Check options with "-- -h".
    """

    parser = argparse.ArgumentParser(prog=f"{Path(sys.argv[0]).name} -s docs")
    parser.add_argument("--serve", action="store_true", help="Serve the docs")
    args = parser.parse_args(session.posargs)

    session.install(SKBUILD_CORE_REQ)
    session.install("-e.[docs]")

    session.chdir("docs")
    shutil.rmtree("_build", ignore_errors=True)
    session.run("sphinx-build", "-M", "html", ".", "_build", "-W")

    if args.serve:
        print("Launching docs at http://localhost:8000/ - use Ctrl-C to quit")
        session.run("python", "-m", "http.server", "8000", "-d", "_build/html")


@nox.session(default=False)
def build(session):
    """
    Make an SDist and a wheel.
    """

    session.install("build")
    session.run("python", "-m", "build")


@nox.session(reuse_venv=True, default=False)
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


# Sample projects that build with classic scikit-build (the core-*, hatchling-*,
# and pi-fortran projects do not use the skbuild setup() wrapper; tower-of-babel
# has no pyproject.toml and needs Boost, so it can't build in isolation).
SAMPLE_PROJECTS = [
    "hello-cpp",
    "hello-pure",
    "hello-cython",
    "hello-pybind11",
    "pen2-cython",
]
if not sys.platform.startswith("win"):
    # hello-cmake-package's "hello" SHARED library exports no symbols, so MSVC
    # produces no import library and the extension can't link against it. The
    # sample-projects noxfile skips it on Windows for the same reason.
    SAMPLE_PROJECTS.append("hello-cmake-package")


@nox.session(default=False)
def sample_projects(session: nox.Session) -> None:
    """
    Build the scikit-build-sample-projects against this checkout. Pass the path
    to a scikit-build-sample-projects checkout (default: ./scikit-build-sample-projects).
    """

    parser = argparse.ArgumentParser(prog=f"{Path(sys.argv[0]).name} -s sample_projects")
    parser.add_argument(
        "path",
        nargs="?",
        default="scikit-build-sample-projects",
        help="Location of a scikit-build-sample-projects checkout",
    )
    args = parser.parse_args(session.posargs)
    projects_dir = Path(args.path).resolve() / "projects"

    tmp_dir = Path(session.create_tmp()).resolve()
    wheelhouse = tmp_dir / "wheelhouse"

    session.install("build", "pip")
    session.run(
        "python",
        "-m",
        "pip",
        "wheel",
        "--no-cache-dir",
        "--wheel-dir",
        str(wheelhouse),
        ".",
        SKBUILD_CORE_REQ,
    )
    session.run(
        "python",
        "-m",
        "pip",
        "download",
        "--dest",
        str(wheelhouse),
        "setuptools",
        "wheel",
        "cmake",
        "ninja",
        "cython",
        "pybind11",
        "numpy",
    )

    # Force the sample projects' "scikit-build" build requirement onto the
    # local wheel by resolving everything from the wheelhouse.
    env = {"PIP_NO_INDEX": "1", "PIP_FIND_LINKS": str(wheelhouse)}
    for project in SAMPLE_PROJECTS:
        session.run(
            "python",
            "-m",
            "build",
            "--wheel",
            "--outdir",
            str(tmp_dir / "dist" / project),
            str(projects_dir / project),
            env=env,
        )


@nox.session(reuse_venv=True, default=False)
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
    session.install(SKBUILD_CORE_REQ)
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
