"""
This module defines constants commonly used in scikit-build.
"""

import os

SKBUILD_DIR = "_skbuild"
CMAKE_BUILD_DIR = os.path.join(SKBUILD_DIR, "cmake-build")
CMAKE_INSTALL_DIR = os.path.join(SKBUILD_DIR, "cmake-install")
SETUPTOOLS_INSTALL_DIR = os.path.join(SKBUILD_DIR, "setuptools")
