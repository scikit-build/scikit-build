"""This module defines custom implementation of ``build`` setuptools command."""

import setuptools  # noqa: F401
from distutils.command.build import build as _build

from . import set_build_base_mixin


# TODO: setuptools stubs
class build(set_build_base_mixin, _build):
    """Custom implementation of ``build`` setuptools command."""
