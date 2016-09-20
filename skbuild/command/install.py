"""This module defines custom implementation of ``install`` setuptools
command."""

from setuptools.command.install import install as _install

from . import set_build_base_mixin
from ..utils import new_style


class install(set_build_base_mixin, new_style(_install)):
    """Custom implementation of ``install`` setuptools command."""
    pass
