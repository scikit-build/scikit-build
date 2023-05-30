"""This module defines object specific to AIX platform."""

from __future__ import annotations

import sys
import textwrap

from . import unix


class AIXPlatform(unix.UnixPlatform):
    """AIX implementation of :class:`.abstract.CMakePlatform`."""

    @property
    def generator_installation_help(self) -> str:
        """Return message guiding the user for installing a valid toolchain."""
        return (
            textwrap.dedent(
                """
            Building AIX wheels for Python {pyver} requires IBM XL C/C++.
            Get it here:

              https://www.ibm.com/products/xl-c-aix-compiler-power
            """
            )
            .format(pyver=".".join(str(v) for v in sys.version_info[:2]))
            .strip()
        )
