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
CMAKE_BUILD_DIR = os.path.join(SKBUILD_DIR, "cmake-build")
CMAKE_INSTALL_DIR = os.path.join(SKBUILD_DIR, "cmake-install")
SETUPTOOLS_INSTALL_DIR = os.path.join(SKBUILD_DIR, "setuptools")
