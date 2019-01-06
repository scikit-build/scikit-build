"""This module defines custom implementation of ``build_ext`` setuptools command."""

try:
    from setuptools.command.build_ext import build_ext as _build_ext
except ImportError:
    from distutils.command.build_ext import build_ext as _build_ext

from . import set_build_base_mixin
from ..utils import new_style


class build_ext(set_build_base_mixin, new_style(_build_ext)):
    """Custom implementation of ``build_ext`` setuptools command."""
