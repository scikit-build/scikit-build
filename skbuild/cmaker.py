"""
Compatibility shim for ``skbuild.cmaker``.

scikit-build 1.0 builds on scikit-build-core and no longer ships the ``CMaker``
class. Only :func:`get_cmake_version` is kept, since downstream ``setup.py``
files use it to gate on the installed CMake version.
"""

from __future__ import annotations

import warnings
from pathlib import Path

from scikit_build_core.program_search import get_cmake_program, get_cmake_programs

from .exceptions import SKBuildError

__all__ = ["get_cmake_version"]

warnings.warn(
    "skbuild.cmaker is a compatibility shim for scikit-build <1.0; only "
    "get_cmake_version is provided. Port to scikit-build-core APIs.",
    DeprecationWarning,
    stacklevel=2,
)


def get_cmake_version(cmake_executable: str = "") -> str:
    """
    Return the version of the given (or first found) CMake, e.g. ``"3.14.4"``.

    With no argument, searches the way scikit-build-core does: the ``cmake``
    PyPI package if installed, then ``cmake3`` and ``cmake`` on PATH.
    Pre-release suffixes are dropped (``3.30.0-rc1`` reports as ``3.30.0``).

    Raises :class:`skbuild.exceptions.SKBuildError` if CMake cannot be run.
    """
    msg = f"Problem with the CMake installation, aborting build. CMake executable is {cmake_executable or 'cmake'}"
    try:
        if cmake_executable:
            program = get_cmake_program(Path(cmake_executable))
        else:
            program = next((p for p in get_cmake_programs(module=True) if p.version is not None), None)
    except OSError as err:
        raise SKBuildError(msg) from err
    if program is None or program.version is None:
        raise SKBuildError(msg)
    return str(program.version)
