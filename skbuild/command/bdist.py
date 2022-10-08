"""This module defines custom implementation of ``bdist`` setuptools command."""

import setuptools  # noqa: F401
from distutils.command.bdist import bdist as _bdist

from . import set_build_base_mixin


class bdist(set_build_base_mixin, _bdist):
    """Custom implementation of ``bdist`` setuptools command."""
