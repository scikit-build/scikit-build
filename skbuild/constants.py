"""
This module defines constants commonly used in scikit-build.
"""

from __future__ import annotations

import contextlib
import functools
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from distutils.util import get_platform
from packaging.version import InvalidVersion, Version


@functools.lru_cache(maxsize=None)
def get_cmake_version(cmake_path: os.PathLike[str] | str) -> Version:
    try:
        result = subprocess.run([str(cmake_path), "-E", "capabilities"], capture_output=True, text=True, check=False)
        with contextlib.suppress(json.decoder.JSONDecodeError, KeyError, InvalidVersion):
            return Version(json.loads(result.stdout)["version"]["string"])
    except subprocess.CalledProcessError:
        # In some cases (like Pyodide<0.26's cmake wrapper), `-E` isn't handled
        # correctly, so let's try `--version`, which is more common so more
        # likely to be wrapped correctly
        with contextlib.suppress(subprocess.CalledProcessError):
            result = subprocess.run([str(cmake_path), "--version"], capture_output=True, text=True, check=False)
            with contextlib.suppress(IndexError, InvalidVersion):
                return Version(result.stdout.splitlines()[0].split()[-1].split("-")[0])
    except PermissionError:
        pass

    return Version("0.0")


def _get_cmake_executable() -> str:
    with contextlib.suppress(ImportError):
        from cmake import CMAKE_BIN_DIR  # pylint: disable=import-outside-toplevel

        path = f"{CMAKE_BIN_DIR}/cmake"
        if Path(f"{path}.exe").is_file():
            return f"{path}.exe"
        return path

    for name in ("cmake", "cmake3"):
        prog = shutil.which(name)
        if prog and get_cmake_version(prog) >= Version("3.5"):
            return prog

    # Just guess otherwise
    return "cmake"


CMAKE_DEFAULT_EXECUTABLE = _get_cmake_executable()
"""Default path to CMake executable."""


def _default_skbuild_plat_name() -> str:
    """Get default platform name.

    On linux and windows, it corresponds to :func:`distutils.util.get_platform()`.

    On macOS, it corresponds to the version and machine associated with :func:`platform.mac_ver()`.
    """
    if not sys.platform.startswith("darwin"):
        return get_platform()

    supported_macos_architectures = {"x86_64", "arm64"}
    macos_universal2_architectures = {"x86_64", "arm64"}

    # See https://github.com/scikit-build/scikit-build/issues/643 for a weird cross
    # compiling bug that forces us to avoid getting machine from platform.mac_ver()[2]
    release = platform.mac_ver()[0]
    machine = platform.machine()

    # If the MACOSX_DEPLOYMENT_TARGET environment variable is defined, use
    # it, as it will be the most accurate. Otherwise use the value returned by
    # platform.mac_ver() provided by the platform module available in the
    # Python standard library.
    #
    # Note that on macOS, distutils.util.get_platform() is not used because
    # it returns the macOS version on which Python was built which may be
    # significantly older than the user's current machine.
    release = os.environ.get("MACOSX_DEPLOYMENT_TARGET", "") or release
    major_macos, minor_macos = release.split(".")[:2]

    # On macOS 11+, only the major version matters.
    if int(major_macos) >= 11:
        minor_macos = "0"

    # Use CMAKE_OSX_ARCHITECTURES if that is set, otherwise use ARCHFLAGS,
    # which is the variable used by Setuptools. Fall back to the machine arch
    # if neither of those is given. Not that -D flags like CMAKE_SYSTEM_PROCESSOR
    # will override this by setting it later.

    archflags = os.environ.get("ARCHFLAGS")
    if archflags is not None:
        machine = ";".join(set(archflags.split()) & supported_macos_architectures)

    machine = os.environ.get("CMAKE_OSX_ARCHITECTURES", machine)

    # Handle universal2 wheels, if those two architectures are requested.
    if set(machine.split(";")) == macos_universal2_architectures:
        machine = "universal2"

    return f"macosx-{major_macos}.{minor_macos}-{machine}"


_SKBUILD_PLAT_NAME = _default_skbuild_plat_name()


def set_skbuild_plat_name(plat_name: str) -> None:
    """Set platform name associated with scikit-build functions returning a path:

    * :func:`SKBUILD_DIR()`
    * :func:`SKBUILD_MARKER_FILE()`
    * :func:`CMAKE_BUILD_DIR()`
    * :func:`CMAKE_INSTALL_DIR()`
    * :func:`CMAKE_SPEC_FILE()`
    * :func:`SETUPTOOLS_INSTALL_DIR()`
    """
    global _SKBUILD_PLAT_NAME  # noqa: PLW0603
    _SKBUILD_PLAT_NAME = plat_name


def skbuild_plat_name() -> str:
    """Get platform name formatted as `<operating_system>[-<operating_system_version>]-<machine_architecture>`.

    Default value corresponds to :func:`_default_skbuild_plat_name()` and can be overridden
    with :func:`set_skbuild_plat_name()`.

    Examples of values are `macosx-10.9-x86_64`, `linux-x86_64`, `linux-i686` or `win-am64`.
    """
    return _SKBUILD_PLAT_NAME


def SKBUILD_DIR() -> str:
    """Top-level directory where setuptools and CMake directories are generated."""
    version_str = ".".join(map(str, sys.version_info[:2]))
    return os.path.join("_skbuild", f"{_SKBUILD_PLAT_NAME}-{version_str}")


def SKBUILD_MARKER_FILE() -> str:
    """Marker file used by :func:`skbuild.command.generate_source_manifest.generate_source_manifest.run()`."""
    return os.path.join(SKBUILD_DIR(), "_skbuild_MANIFEST")


def CMAKE_BUILD_DIR() -> str:
    """CMake build directory."""
    return os.path.join(SKBUILD_DIR(), "cmake-build")


def CMAKE_INSTALL_DIR() -> str:
    """CMake install directory."""
    return os.path.join(SKBUILD_DIR(), "cmake-install")


def CMAKE_SPEC_FILE() -> str:
    """CMake specification file storing CMake version, CMake configuration arguments and
    environment variables ``PYTHONNOUSERSITE`` and ``PYTHONPATH``.
    """
    return os.path.join(CMAKE_BUILD_DIR(), "CMakeSpec.json")


def SETUPTOOLS_INSTALL_DIR() -> str:
    """Setuptools install directory."""
    return os.path.join(SKBUILD_DIR(), "setuptools")
