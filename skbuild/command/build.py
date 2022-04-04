"""This module defines custom implementation of ``build`` setuptools command."""

try:
    from setuptools.command.build import build as _build
except ImportError:
    from distutils.command.build import build as _build

from . import set_build_base_mixin


class build(set_build_base_mixin, _build):
    """Custom implementation of ``build`` setuptools command."""
