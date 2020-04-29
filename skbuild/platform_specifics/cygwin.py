"""This module defines object specific to Cygwin platform."""

import sys
import textwrap

from . import abstract
from .abstract import CMakeGenerator


# pylint:disable=abstract-method
class CygwinPlatform(abstract.CMakePlatform):
    """Cygwin implementation of :class:`.abstract.CMakePlatform`."""

    def __init__(self):
        super(CygwinPlatform, self).__init__()
        self.default_generators = [CMakeGenerator("Ninja"), CMakeGenerator("Unix Makefiles")]

    @property
    def generator_installation_help(self):
        """Return message guiding the user for installing a valid toolchain."""
        return (
            textwrap.dedent(
                """
            Building Cygwin wheels for Python {pyver} requires Cygwin packages
            ninja or make and compilers from e.g. gcc-core and gcc-g++.
            Get them here:

              https://cygwin.com/packages/package_list.html
            """
            )
            .format(pyver="%s.%s" % sys.version_info[:2])
            .strip()
        )
