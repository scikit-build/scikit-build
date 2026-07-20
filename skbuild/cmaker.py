"""
Compatibility shim for ``skbuild.cmaker``.

scikit-build 1.0 builds on scikit-build-core and no longer ships the ``CMaker``
class. Only :func:`get_cmake_version` is kept, since downstream ``setup.py``
files use it to gate on the installed CMake version.
"""

from __future__ import annotations

import shutil
import subprocess
import warnings

from .exceptions import SKBuildError

__all__ = ["get_cmake_version"]

warnings.warn(
    "skbuild.cmaker is a compatibility shim for scikit-build <1.0; only "
    "get_cmake_version is provided. Port to scikit-build-core APIs.",
    DeprecationWarning,
    stacklevel=2,
)


def _default_cmake_executable() -> str:
    for name in ("cmake", "cmake3"):
        prog = shutil.which(name)
        if prog:
            return prog
    return "cmake"


def get_cmake_version(cmake_executable: str = "") -> str:
    """
    Return the version reported by ``cmake --version``, e.g. ``"3.14.4"``.

    Raises :class:`skbuild.exceptions.SKBuildError` if CMake cannot be run.
    """
    cmake_executable = cmake_executable or _default_cmake_executable()
    try:
        version_string_bytes = subprocess.run(
            [cmake_executable, "--version"], check=True, stdout=subprocess.PIPE
        ).stdout
    except (OSError, subprocess.CalledProcessError) as err:
        msg = f"Problem with the CMake installation, aborting build. CMake executable is {cmake_executable}"
        raise SKBuildError(msg) from err

    return version_string_bytes.decode().splitlines()[0].split(" ")[-1]
