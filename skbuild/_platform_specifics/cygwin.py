"""This module defines object specific to Cygwin platform."""

from __future__ import annotations

import sys
import textwrap

from . import abstract
from .abstract import CMakeGenerator


class CygwinPlatform(abstract.CMakePlatform):
    """Cygwin implementation of :class:`.abstract.CMakePlatform`."""

    def __init__(self) -> None:
        super().__init__()
        self.default_generators = [CMakeGenerator("Ninja"), CMakeGenerator("Unix Makefiles")]

    @property
    def generator_installation_help(self) -> str:
        """Return message guiding the user for installing a valid toolchain."""

        pyver = ".".join(str(v) for v in sys.version_info[:2])
        return textwrap.dedent(
            f"""\
            Building Cygwin wheels for Python {pyver} requires Cygwin packages
            ninja or make and compilers from e.g. gcc-core and gcc-g++.
            Get them here:

              https://cygwin.com/packages/package_list.html"""
        )
