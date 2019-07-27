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
    if sys.platform == 'darwin':
        # If the MACOSX_DEPLOYMENT_TARGET environment variable is defined, use
        # it, as it will be the most accurate. Otherwise use the value returned
        # by platform.mac_ver() provided by the platform module available in
        # the Python standard library.
        #
        # Note that on macOS, distutils.util.get_platform() is not used because
        # it returns the macOS version on which Python was built which may be
        # significantly older than the user's current machine.
        release, _, machine = platform.mac_ver()
        release = os.environ.get("MACOSX_DEPLOYMENT_TARGET", release)
        split_ver = release.split('.')
        return 'macosx-{}.{}-{}'.format(split_ver[0], split_ver[1], machine)
    else:
        return get_platform()


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
    global _SKBUILD_PLAT_NAME
    _SKBUILD_PLAT_NAME = plat_name


def skbuild_plat_name():
    """Get platform name formatted as `<operating_system>[-<operating_system_version>]-<machine_architecture>`.

    Default value corresponds to :func:`_default_skbuild_plat_name()` and can be overridden
    with :func:`set_skbuild_plat_name()`.

    Examples of values are `macosx-10.6-x86_64`, `linux-x86_64`, `linux-i686` or `win-am64`.
    """
    return _SKBUILD_PLAT_NAME


def SKBUILD_DIR():
    """Top-level directory where setuptools and CMake directories are generated."""
    return os.path.join(
        "_skbuild",
        "{}-{}".format(_SKBUILD_PLAT_NAME, '.'.join(map(str, sys.version_info[:2]))),
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
