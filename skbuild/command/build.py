"""This module defines custom implementation of ``build`` setuptools command."""

try:
    from setuptools.command.build import build as _build
except ImportError:
    from distutils.command.build import build as _build

from . import set_build_base_mixin
from ..utils import new_style


class build(set_build_base_mixin, new_style(_build)):
    """Custom implementation of ``build`` setuptools command."""
    pass
