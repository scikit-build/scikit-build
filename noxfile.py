import os
import sys

import nox

nox.options.sessions = ["lint", "tests"]

PYTHON_ALL_VERSIONS = ["3.6", "3.7", "3.8", "3.9", "3.10", "3.11", "pypy3.7", "pypy3.8", "pypy3.9"]
MSVC_ALL_VERSIONS = {"2017", "2019", "2022"}

if os.environ.get("CI", None):
    nox.options.error_on_missing_interpreters = True


@nox.session
def lint(session):
    """
    Run the linters.
    """
    session.install("pre-commit")
    session.run("pre-commit", "run", "-a")


@nox.session(python=PYTHON_ALL_VERSIONS)
def tests(session):
    """
    Run the tests.
    """
    posargs = list(session.posargs) or ["--cov", "--cov-report=xml"]
    env = os.environ.copy()

    # This should be handled via markers or some other pytest mechanism, but for now, this is usable.
    # nox -s tests-3.9 -- 2017 2019
    if sys.platform.startswith("win") and MSVC_ALL_VERSIONS & set(posargs):
        known_MSVC = {arg for arg in posargs if arg in MSVC_ALL_VERSIONS}
        posargs = [arg for arg in posargs if arg not in MSVC_ALL_VERSIONS]
        for version in MSVC_ALL_VERSIONS:
            contained = "1" if version in known_MSVC else "0"
            env[f"SKBUILD_TEST_FIND_VS{version}_INSTALLATION_EXPECTED"] = contained

    # Latest versions may break things, so grab them for testing!
    session.install("-U", "setuptools", "wheel")
    session.install("-e", ".[test,cov,doctest]")
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
    Build the docs.
    """

    session.install(".[docs]")

    session.chdir("docs")
    session.run("sphinx-build", "-M", "html", ".", "_build")

    if session.posargs:
        if "serve" in session.posargs:
            print("Launching docs at http://localhost:8000/ - use Ctrl-C to quit")
            session.run("python", "-m", "http.server", "8000", "-d", "_build/html")
        else:
            print("Unsupported argument to docs")


@nox.session
def build(session):
    """
    Make an SDist and a wheel.
    """

    session.install("build")
    session.run("python", "-m", "build")
