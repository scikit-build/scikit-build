"""Deprecated public alias for :mod:`skbuild._utils`.

This module is removed in the next major release, when scikit-build-core's
setuptools plugin becomes the backend. Importing it emits a
:class:`~skbuild.exceptions.SKBuildDeprecationWarning`.
"""

from __future__ import annotations

import warnings

from .._utils import (
    CommonLog,
    Distribution,
    OptStr,
    PythonModuleFinder,
    Self,
    distribution_hide_listing,
    logger,
    mkdir_p,
    parse_manifestin,
    push_dir,
    to_platform_path,
    to_unix_path,
)
from ..exceptions import SKBuildDeprecationWarning

__all__ = [
    "CommonLog",
    "Distribution",
    "OptStr",
    "PythonModuleFinder",
    "Self",
    "distribution_hide_listing",
    "logger",
    "mkdir_p",
    "parse_manifestin",
    "push_dir",
    "to_platform_path",
    "to_unix_path",
]

warnings.warn(
    "skbuild.utils is deprecated and will be removed in the next major release, when "
    "scikit-build-core's setuptools backend takes over; switch to scikit-build-core.",
    SKBuildDeprecationWarning,
    stacklevel=2,
)
