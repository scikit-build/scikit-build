"""
This module defines constants commonly used in scikit-build.
"""

import os
import sys

from distutils.util import get_platform

SKBUILD_DIR = os.path.join(
    "_skbuild",
    "{}-{}".format(get_platform(), '.'.join(map(str, sys.version_info[:2]))),
)
"""Top-level directory where setuptools and CMake directories are generated."""

CMAKE_BUILD_DIR = os.path.join(SKBUILD_DIR, "cmake-build")
"""CMake build directory."""

CMAKE_INSTALL_DIR = os.path.join(SKBUILD_DIR, "cmake-install")
"""CMake install directory."""

CMAKE_SPEC_FILE = os.path.join(CMAKE_BUILD_DIR, "CMakeSpec.json")
"""CMake specification file storing CMake version and CMake configuration arguments."""

SETUPTOOLS_INSTALL_DIR = os.path.join(SKBUILD_DIR, "setuptools")
"""Setuptools install directory."""
