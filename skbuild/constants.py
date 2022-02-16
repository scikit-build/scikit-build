"""
This module defines constants commonly used in scikit-build.
"""

import os
import platform
import sys
from distutils.util import get_platform

CMAKE_DEFAULT_EXECUTABLE = "cmake"
"""Default path to CMake executable."""


def _default_skbuild_plat_name():
    """Get default platform name.

    On linux and windows, it corresponds to :func:`distutils.util.get_platform()`.

    On macOS, it corresponds to the version and machine associated with :func:`platform.mac_ver()`.
    """
    if sys.platform != "darwin":
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
    release = os.environ.get("MACOSX_DEPLOYMENT_TARGET", release)
    major_macos, minor_macos = release.split(".")[:2]

    # On macOS 11+, only the major version matters.
    if int(major_macos) >= 11:
        minor_macos = "0"

    # Use CMAKE_OSX_ARCHITECTURES if that is set, otherwise use ARCHFLAGS,
    # which is the variable used by Setuptools. Fall back to the machine arch
    # if neither of those is given.

    archflags = os.environ.get("ARCHFLAGS")
    if archflags is not None:
        machine = ";".join(set(archflags.split()) & supported_macos_architectures)

    machine = os.environ.get("CMAKE_OSX_ARCHITECTURES", machine)

    # Handle universal2 wheels, if those two architectures are requested.
    if set(machine.split(";")) == macos_universal2_architectures:
        machine = "universal2"

    return "macosx-{}.{}-{}".format(major_macos, minor_macos, machine)


_SKBUILD_PLAT_NAME = _default_skbuild_plat_name()


def set_skbuild_plat_name(plat_name):
    """Set platform name associated with scikit-build functions returning a path:

    * :func:`SKBUILD_DIR()`
    * :func:`SKBUILD_MARKER_FILE()`
    * :func:`CMAKE_BUILD_DIR()`
    * :func:`CMAKE_INSTALL_DIR()`
    * :func:`CMAKE_SPEC_FILE()`
    * :func:`SETUPTOOLS_INSTALL_DIR()`
    """
    global _SKBUILD_PLAT_NAME  # pylint: disable=global-statement
    _SKBUILD_PLAT_NAME = plat_name


def skbuild_plat_name():
    """Get platform name formatted as `<operating_system>[-<operating_system_version>]-<machine_architecture>`.

    Default value corresponds to :func:`_default_skbuild_plat_name()` and can be overridden
    with :func:`set_skbuild_plat_name()`.

    Examples of values are `macosx-10.9-x86_64`, `linux-x86_64`, `linux-i686` or `win-am64`.
    """
    return _SKBUILD_PLAT_NAME


def SKBUILD_DIR():
    """Top-level directory where setuptools and CMake directories are generated."""
    return os.path.join(
        "_skbuild",
        "{}-{}".format(_SKBUILD_PLAT_NAME, ".".join(map(str, sys.version_info[:2]))),
    )


def SKBUILD_MARKER_FILE():
    """Marker file used by :func:`skbuild.command.generate_source_manifest.generate_source_manifest.run()`."""
    return os.path.join(SKBUILD_DIR(), "_skbuild_MANIFEST")


def CMAKE_BUILD_DIR():
    """CMake build directory."""
    return os.path.join(SKBUILD_DIR(), "cmake-build")


def CMAKE_INSTALL_DIR():
    """CMake install directory."""
    return os.path.join(SKBUILD_DIR(), "cmake-install")


def CMAKE_SPEC_FILE():
    """CMake specification file storing CMake version, CMake configuration arguments and
    environment variables ``PYTHONNOUSERSITE`` and ``PYTHONPATH``.
    """
    return os.path.join(CMAKE_BUILD_DIR(), "CMakeSpec.json")


def SETUPTOOLS_INSTALL_DIR():
    """Setuptools install directory."""
    return os.path.join(SKBUILD_DIR(), "setuptools")
