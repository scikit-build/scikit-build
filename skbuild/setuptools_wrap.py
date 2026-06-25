"""Deprecated public alias for :mod:`skbuild._setuptools_wrap`.

This module is removed in the next major release, when scikit-build-core's
setuptools plugin becomes the backend. Import :func:`skbuild.setup` from
``skbuild`` instead. Importing this module emits a
:class:`~skbuild.exceptions.SKBuildDeprecationWarning`.
"""

from __future__ import annotations

import warnings

from ._setuptools_wrap import (
    create_skbuild_argparser,
    get_default_include_package_data,
    parse_args,
    parse_skbuild_args,
    setup,
    strip_package,
)
from .exceptions import SKBuildDeprecationWarning

__all__ = [
    "create_skbuild_argparser",
    "get_default_include_package_data",
    "parse_args",
    "parse_skbuild_args",
    "setup",
    "strip_package",
]

warnings.warn(
    "skbuild.setuptools_wrap is deprecated and will be removed in the next major release, when "
    "scikit-build-core's setuptools backend takes over; import setup from skbuild instead.",
    SKBuildDeprecationWarning,
    stacklevel=2,
)
