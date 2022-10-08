"""This module defines custom implementation of ``build`` setuptools command."""

from setuptools.command.build import build as _build

from . import set_build_base_mixin


# TODO: setuptools stubs
class build(set_build_base_mixin, _build):  # type: ignore[misc]
    """Custom implementation of ``build`` setuptools command."""
