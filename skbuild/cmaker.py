"""Deprecated public alias for :mod:`skbuild._cmaker`.

This module is removed in the next major release, when scikit-build-core's
setuptools plugin becomes the backend. Importing it emits a
:class:`~skbuild.exceptions.SKBuildDeprecationWarning`.
"""

from __future__ import annotations

import warnings

from ._cmaker import CMaker, get_cmake_version, has_cmake_cache_arg, pop_arg
from .exceptions import SKBuildDeprecationWarning

__all__ = ["CMaker", "get_cmake_version", "has_cmake_cache_arg", "pop_arg"]

warnings.warn(
    "skbuild.cmaker is deprecated and will be removed in the next major release, when "
    "scikit-build-core's setuptools backend takes over; switch to scikit-build-core.",
    SKBuildDeprecationWarning,
    stacklevel=2,
)
