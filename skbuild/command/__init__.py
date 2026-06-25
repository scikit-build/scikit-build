"""Deprecated public alias for :mod:`skbuild._command`.

This package is removed in the next major release, when scikit-build-core's
setuptools plugin becomes the backend. Importing it emits a
:class:`~skbuild.exceptions.SKBuildDeprecationWarning`.
"""

from __future__ import annotations

import warnings

from .._command import CommandMixinProtocol, set_build_base_mixin
from ..exceptions import SKBuildDeprecationWarning

__all__ = ["CommandMixinProtocol", "set_build_base_mixin"]

warnings.warn(
    "skbuild.command is deprecated and will be removed in the next major release, when "
    "scikit-build-core's setuptools backend takes over; switch to scikit-build-core.",
    SKBuildDeprecationWarning,
    stacklevel=2,
)
