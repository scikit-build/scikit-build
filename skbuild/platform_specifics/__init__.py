"""Deprecated public alias for :mod:`skbuild._platform_specifics`.

This package is removed in the next major release, when scikit-build-core's
setuptools plugin becomes the backend. Importing it emits a
:class:`~skbuild.exceptions.SKBuildDeprecationWarning`.
"""

from __future__ import annotations

import warnings

from .._platform_specifics import CMakeGenerator, get_platform
from ..exceptions import SKBuildDeprecationWarning

__all__ = ["CMakeGenerator", "get_platform"]

warnings.warn(
    "skbuild.platform_specifics is deprecated and will be removed in the next major release, when "
    "scikit-build-core's setuptools backend takes over; switch to scikit-build-core.",
    SKBuildDeprecationWarning,
    stacklevel=2,
)
