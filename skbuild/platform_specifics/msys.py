"""This module defines object specific to MSYS platform."""

import sys
import textwrap

from . import abstract
from .abstract import CMakeGenerator


# pylint:disable=abstract-method
class MSYSPlatform(abstract.CMakePlatform):
    """MSYS implementation of :class:`.abstract.CMakePlatform`."""

    def __init__(self) -> None:
        super().__init__()
        self.default_generators = [CMakeGenerator("Ninja"), CMakeGenerator("Unix Makefiles")]

    @property
    def generator_installation_help(self) -> str:
        """Return message guiding the user for installing a valid toolchain."""
        return (
            textwrap.dedent(
                """
            Building MSYS wheels for Python {pyver} requires MSYS packages
            ninja or make and compilers from e.g. gcc.
            """
            )
            .format(pyver="%s.%s" % sys.version_info[:2])
            .strip()
        )
