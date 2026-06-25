"""Deprecated public alias for :mod:`skbuild._constants`.

This module is removed in the next major release, when scikit-build-core's
setuptools plugin becomes the backend. Importing it emits a
:class:`~skbuild.exceptions.SKBuildDeprecationWarning`.
"""

from __future__ import annotations

import warnings

from ._constants import (
    CMAKE_BUILD_DIR,
    CMAKE_DEFAULT_EXECUTABLE,
    CMAKE_INSTALL_DIR,
    CMAKE_SPEC_FILE,
    SETUPTOOLS_INSTALL_DIR,
    SKBUILD_DIR,
    SKBUILD_MARKER_FILE,
    get_cmake_version,
    set_skbuild_plat_name,
    skbuild_plat_name,
)
from .exceptions import SKBuildDeprecationWarning

__all__ = [
    "CMAKE_BUILD_DIR",
    "CMAKE_DEFAULT_EXECUTABLE",
    "CMAKE_INSTALL_DIR",
    "CMAKE_SPEC_FILE",
    "SETUPTOOLS_INSTALL_DIR",
    "SKBUILD_DIR",
    "SKBUILD_MARKER_FILE",
    "get_cmake_version",
    "set_skbuild_plat_name",
    "skbuild_plat_name",
]

warnings.warn(
    "skbuild.constants is deprecated and will be removed in the next major release, when "
    "scikit-build-core's setuptools backend takes over; switch to scikit-build-core.",
    SKBuildDeprecationWarning,
    stacklevel=2,
)
