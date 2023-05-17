"""This module defines object specific to SunOS platform."""

from __future__ import annotations

import sys
import textwrap

from . import unix


class SunOSPlatform(unix.UnixPlatform):
    """SunOS implementation of :class:`.abstract.CMakePlatform`."""

    @property
    def generator_installation_help(self) -> str:
        """Return message guiding the user for installing a valid toolchain."""
        return (
            textwrap.dedent(
                """
            Building SunOS wheels for Python {pyver} requires build toolchain.
            It can be installed using:

              pkg install build-essential
            """
            )
            .format(pyver=".".join(str(v) for v in sys.version_info[:2]))
            .strip()
        )
