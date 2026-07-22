# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## What this is

scikit-build (classic) is glue between setuptools and CMake: it lets `setup.py` projects build C/C++/Fortran/Cython extensions with CMake. It is in maintenance mode; new development happens in its successor, scikit-build-core. Supports Python 3.9+ and PyPy.

## Commands

Everything routes through nox (`pipx run nox` works too):

- `nox` — run the default sessions (lint + tests on available Pythons)
- `nox -s tests-3.13` — tests on one Python version
- `nox -s tests-3.13 -- tests/test_hello_cpp.py` — a single test file; pytest args go after `--`
- `nox -s tests -- --cov` — with coverage
- `nox -s lint` — pre-commit (ruff, mypy, codespell, check-sdist, …)
- `nox -s pylint` — pylint (not in the default lint session)
- `nox -s docs -- --serve` — build (and serve) Sphinx docs
- `nox -s build` — SDist + wheel
- `nox -s downstream -- <git-url>` — build a downstream project against this checkout

Tests invoke real CMake builds, so `cmake` (and for some tests ninja, compilers, or gfortran) must be available. Pytest markers gate special cases: `fortran`, `isolated` (downloads deps / builds a wheelhouse, slow), `deprecated`, `nosetuptoolsscm`. Deselect with e.g. `-m "not fortran and not isolated"`. `filterwarnings = error` is set, so new warnings fail tests.

## Architecture

The whole package implements one entry point: `skbuild.setup()` (in `skbuild/setuptools_wrap.py`), a wrapper around `setuptools.setup()`. The flow is:

1. `setuptools_wrap.setup()` strips scikit-build-specific arguments (`cmake_args`, `cmake_source_dir`, `cmake_install_dir`, `cmake_languages`, etc.) and command-line sections (args after `--` separators go to CMake/the build tool), reads `pyproject.toml`, and decides whether CMake is needed.
2. `skbuild/platform_specifics/` picks a working CMake generator for the OS (`platform_factory.get_platform()`; one module per platform — `windows.py` handles Visual Studio discovery).
3. `skbuild/cmaker.py` (`CMaker`) runs CMake configure/build/install into `_skbuild/<platform>-<pyversion>/` (layout defined in `skbuild/constants.py`: `cmake-build/`, `cmake-install/`, `setuptools/`). It injects the shipped CMake modules in `skbuild/resources/cmake/` (`FindPythonExtensions.cmake`, `UseCython.cmake`, `FindF2PY.cmake`, …) onto `CMAKE_MODULE_PATH`.
4. The CMake-installed files are merged into the setuptools package layout, then control passes to setuptools using the overridden command classes in `skbuild/command/` (subclasses of `build`, `build_py`, `build_ext`, `bdist_wheel`, `sdist`, `install`, etc., plus the mixin in `skbuild/command/__init__.py`) so setuptools accounts for CMake-generated files.

Errors are reported via `SKBuildError` (`skbuild/exceptions.py`).

## Tests

`tests/samples/` contains ~30 minimal example projects (hello-cpp, hello-cython, hello-fortran, issue-NNN reproducers, fail-* projects for error paths). Tests copy a sample to a tmp dir (`prepare_project` / fixtures in `tests/__init__.py` and `tests/conftest.py`) and drive a real build via `execute_setup_py`, pip, or `build`. The session-scoped `pep518_wheelhouse` fixture builds a local wheelhouse so isolated builds resolve this checkout instead of PyPI. Assertion helpers live in `tests/pytest_helpers.py`.

## Conventions

- Type checking is strict mypy for `skbuild/` (untyped defs allowed in `tests/`); run via pre-commit.
- Ruff enforces `from __future__ import annotations` in every file; line length 120.
- CI must pass on Python 3.9 — no 3.10+ only constructs.
